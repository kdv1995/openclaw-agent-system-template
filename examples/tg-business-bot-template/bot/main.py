import asyncio
from datetime import datetime, timedelta, timezone
from contextlib import suppress
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from typing import Any

from sqlalchemy import and_, or_, select

from .config import settings
from .db import FollowUp, Lead, SessionLocal, init_db


router = Router()


class LeadFlow(StatesGroup):
    business_type = State()
    role = State()
    monthly_volume = State()
    scale_problem = State()
    has_bot = State()
    current_tools = State()
    urgency = State()
    phone = State()


PROGRESS_TOTAL = 6
MAX_PENDING_FOLLOWUPS = 4


FOLLOWUP_STAGES = {
    "diagnosis_2h": {
        "delay": timedelta(hours=2),
        "text": (
            "Коротке нагадування.\n\n"
            "Ви вже пройшли діагностику. Найкраще зараз не відкладати відео 1: там показано, де бізнес зазвичай губить теплі заявки після першого контакту.\n\n"
            "Якщо актуально, продовжіть з відео або одразу залиште номер для консультації."
        ),
    },
    "video1_20h": {
        "delay": timedelta(hours=20),
        "text": (
            "Повертаюсь з другим кроком.\n\n"
            "Якщо після першого відео стало видно, що follow-up зараз тримається на ручній роботі, наступне відео покаже, як бот може вести людину без тиску: сегментація, FAQ, прогрів і передача менеджеру."
        ),
    },
    "video2_24h": {
        "delay": timedelta(hours=24),
        "text": (
            "Ще один важливий штрих.\n\n"
            "Коли є сегментація, наступне питання — довіра: гарантія, підтримка, вебінари, трекінг заявок і зрозумілий наступний крок. Це тема третього відео."
        ),
    },
    "faq_36h": {
        "delay": timedelta(hours=36),
        "text": (
            "Бачу, що ви дивились FAQ.\n\n"
            "Якщо головне питання зараз не “що таке бот”, а “чи окупиться система саме в нашому процесі”, краще розібрати це на короткій консультації: заявки, сегменти, follow-up і перший процес для автоматизації."
        ),
    },
    "consultation_3h": {
        "delay": timedelta(hours=3),
        "text": (
            "М'яке нагадування про консультацію.\n\n"
            "Якщо зручно, залиште номер. На дзвінку не треба буде пояснювати все з нуля: бот вже збере тип бізнесу, вузьке місце, інструменти і рівень готовності."
        ),
    },
    "nurture_3d": {
        "delay": timedelta(days=3),
        "text": (
            "Повертаюсь з практичним питанням.\n\n"
            "Якби сьогодні треба було автоматизувати тільки одну річ, що болить сильніше: не дотискаються ліди, багато повторних питань, немає прогріву чи не видно статусів покупок?"
        ),
    },
}


def keyboard(items: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=text, callback_data=data)] for text, data in items]
    )


def grid_keyboard(items: list[tuple[str, str]], columns: int = 2) -> InlineKeyboardMarkup:
    rows = []
    for index in range(0, len(items), columns):
        rows.append([InlineKeyboardButton(text=text, callback_data=data) for text, data in items[index : index + columns]])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Надіслати номер телефону", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def followup_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="▶️ Продовжити відео", callback_data="video:1"),
                InlineKeyboardButton(text="📞 Консультація", callback_data="consultation:start"),
            ],
            [InlineKeyboardButton(text="Не нагадувати", callback_data="followup:stop")],
        ]
    )


def first_name(event: Any) -> str:
    name = getattr(event.from_user, "first_name", None) or "вітаю"
    return name.strip()


def progress(step: int) -> str:
    filled = "●" * step
    empty = "○" * (PROGRESS_TOTAL - step)
    return f"{filled}{empty}  {step}/{PROGRESS_TOTAL}"


def diagnostic_header(step: int, title: str) -> str:
    return f"{progress(step)}\n{title}\n"


def business_label(value: str | None) -> str:
    labels = {
        "services": "експертному або сервісному бізнесі",
        "ecommerce": "товарному бізнесі",
        "education": "освітньому продукті",
        "b2b": "B2B-продажах",
        "other": "бізнесі зі своєю специфікою",
    }
    return labels.get(value or "", "бізнесі")


def problem_insight(value: str | None) -> str:
    insights = {
        "followup": "Головний фокус — не втрачати теплих людей після першої заявки. Тут найшвидше дає ефект автоматичний follow-up.",
        "support": "Головний фокус — зняти повторювані питання з команди, але не зробити спілкування холодним.",
        "warmup": "Головний фокус — побудувати прогрів, який веде людину до рішення без тиску і хаосу в повідомленнях.",
        "tracking": "Головний фокус — бачити шлях людини від заявки до покупки, щоб не керувати продажами на відчуттях.",
    }
    return insights.get(value or "", "Головний фокус — зібрати заявки, прогрів і передачу в продажі в одну зрозумілу систему.")


def volume_insight(value: str | None) -> str:
    insights = {
        "low": "На цьому етапі важливо не ускладнити систему: краще легкий бот, чиста база і правильні сценарії.",
        "mid": "Тут вже є сенс будувати нормальну сегментацію, бо ручний follow-up починає з'їдати продажі.",
        "high": "При такому обсязі потрібна дисципліна даних: сегменти, статуси, нагадування і чіткий handoff менеджеру.",
        "unknown": "Якщо обсяг важко порахувати, перший крок — зробити систему, яка почне рахувати заявки й статуси автоматично.",
    }
    return insights.get(value or "", "")


def tools_choice_label(value: str | None) -> str:
    labels = {
        "manual_messengers": "менеджери і месенджери вручну",
        "sheets": "таблиці / Excel / Google Sheets",
        "crm": "CRM або pipeline продажів",
        "bot_basic": "простий бот без нормальної логіки",
        "ads_direct": "Instagram / Telegram / Direct як основний канал",
        "site_forms": "лендінг або сайт із формами",
        "payments_tracking": "оплати, статуси покупок або кабінет клієнта",
        "mixed": "змішана система з кількох інструментів",
    }
    return labels.get(value or "", value or "")


async def move_to_urgency(event: Any, state: FSMContext) -> None:
    target = getattr(event, "message", event)
    await state.set_state(LeadFlow.urgency)
    await target.answer(
        "Я зібрав базову картину.\n\n"
        "Останній штрих — темп. Це допоможе зрозуміти, чи вам потрібен швидкий запуск, чи спочатку м'який прогрів і план.\n\n"
        "Наскільки швидко треба навести порядок?",
        reply_markup=grid_keyboard(
            [
                ("⚡️ Запускати зараз", "urgency:now"),
                ("📅 За 2-4 тижні", "urgency:soon"),
                ("👀 Поки вивчаю", "urgency:research"),
            ]
        ),
    )


async def upsert_lead(event: Any, **fields: str) -> None:
    user = event.from_user
    async with SessionLocal() as session:
        result = await session.execute(select(Lead).where(Lead.telegram_id == user.id))
        lead = result.scalar_one_or_none()
        if lead is None:
            lead = Lead(
                telegram_id=user.id,
                username=user.username,
                full_name=user.full_name,
            )
            session.add(lead)
        for key, value in fields.items():
            setattr(lead, key, value)
        await session.commit()


async def get_lead_by_event(event: Any) -> Lead | None:
    user = event.from_user
    async with SessionLocal() as session:
        result = await session.execute(select(Lead).where(Lead.telegram_id == user.id))
        return result.scalar_one_or_none()


async def cancel_pending_followups(telegram_id: int, reason: str = "cancelled") -> int:
    async with SessionLocal() as session:
        result = await session.execute(
            select(FollowUp).where(
                and_(FollowUp.telegram_id == telegram_id, FollowUp.status == "pending")
            )
        )
        followups = list(result.scalars())
        for item in followups:
            item.status = reason
        await session.commit()
        return len(followups)


async def schedule_followups(event: Any, stages: list[str], reset_pending: bool = False) -> None:
    lead = await get_lead_by_event(event)
    if lead is None or lead.followup_opt_out or lead.phone:
        return
    now = datetime.now(timezone.utc)
    async with SessionLocal() as session:
        result = await session.execute(select(Lead).where(Lead.telegram_id == lead.telegram_id))
        db_lead = result.scalar_one_or_none()
        if db_lead is None or db_lead.followup_opt_out or db_lead.phone:
            return
        if reset_pending:
            pending_result = await session.execute(
                select(FollowUp).where(
                    and_(FollowUp.lead_id == db_lead.id, FollowUp.status == "pending")
                )
            )
            for item in pending_result.scalars():
                item.status = "rescheduled"
        pending_count_result = await session.execute(
            select(FollowUp).where(and_(FollowUp.lead_id == db_lead.id, FollowUp.status == "pending"))
        )
        pending_count = len(list(pending_count_result.scalars()))
        for stage in stages:
            if pending_count >= MAX_PENDING_FOLLOWUPS:
                break
            config = FOLLOWUP_STAGES[stage]
            duplicate_result = await session.execute(
                select(FollowUp).where(and_(FollowUp.lead_id == db_lead.id, FollowUp.stage == stage))
            )
            duplicate = duplicate_result.scalar_one_or_none()
            scheduled_at = now + config["delay"]
            if duplicate is not None and duplicate.status == "sent":
                continue
            if duplicate is not None:
                duplicate.status = "pending"
                duplicate.message_text = config["text"]
                duplicate.scheduled_at = scheduled_at
                duplicate.error = None
                duplicate.sent_at = None
                pending_count += 1
                continue
            session.add(
                FollowUp(
                    lead_id=db_lead.id,
                    telegram_id=db_lead.telegram_id,
                    stage=stage,
                    message_text=config["text"],
                    scheduled_at=scheduled_at,
                )
            )
            pending_count += 1
        await session.commit()


async def mark_followup_sent(followup_id: int, stage: str, telegram_id: int) -> None:
    async with SessionLocal() as session:
        result = await session.execute(select(FollowUp).where(FollowUp.id == followup_id))
        followup = result.scalar_one_or_none()
        if followup is not None:
            followup.status = "sent"
            followup.sent_at = datetime.now(timezone.utc)
        lead_result = await session.execute(select(Lead).where(Lead.telegram_id == telegram_id))
        lead = lead_result.scalar_one_or_none()
        if lead is not None:
            lead.last_followup_stage = stage
        await session.commit()


async def mark_followup_failed(followup_id: int, error: str) -> None:
    async with SessionLocal() as session:
        result = await session.execute(select(FollowUp).where(FollowUp.id == followup_id))
        followup = result.scalar_one_or_none()
        if followup is not None:
            followup.status = "failed"
            followup.error = error[:1000]
        await session.commit()


async def run_followup_once(bot: Bot, limit: int = 20) -> int:
    now = datetime.now(timezone.utc)
    async with SessionLocal() as session:
        result = await session.execute(
            select(FollowUp, Lead)
            .join(Lead, Lead.id == FollowUp.lead_id)
            .where(
                and_(
                    FollowUp.status == "pending",
                    FollowUp.scheduled_at <= now,
                    Lead.followup_opt_out == 0,
                    Lead.phone.is_(None),
                    or_(Lead.intent.is_(None), Lead.intent != "consultation_requested"),
                )
            )
            .order_by(FollowUp.scheduled_at.asc())
            .limit(limit)
        )
        due = list(result.all())
    for followup, lead in due:
        try:
            if not settings.followup_test_mode:
                await bot.send_message(
                    chat_id=lead.telegram_id,
                    text=followup.message_text,
                    reply_markup=followup_keyboard(),
                )
            await mark_followup_sent(followup.id, followup.stage, lead.telegram_id)
        except Exception as exc:
            await mark_followup_failed(followup.id, str(exc))
    return len(due)


async def followup_worker(bot: Bot) -> None:
    while True:
        await run_followup_once(bot)
        await asyncio.sleep(settings.followup_poll_seconds)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.set_state(LeadFlow.business_type)
    await state.set_data({})
    await upsert_lead(message, followup_opt_out=0)
    await message.answer(
        f"Вітаю, {first_name(message)}.\n\n"
        "Я проведу коротку діагностику системи масштабування. Без довгої анкети: тільки те, що впливає на заявки, прогрів, продажі і повторні покупки.\n\n"
        "Наприкінці дам ваш маршрут: 3 короткі відео і наступний крок, якщо в системі є потенціал для росту.\n\n"
        f"{diagnostic_header(1, 'Профіль бізнесу')}\n"
        "Що найближче описує ваш бізнес?",
        reply_markup=grid_keyboard(
            [
                ("🧠 Послуги / експерт", "business:services"),
                ("🛒 E-commerce", "business:ecommerce"),
                ("🎓 Освіта / вебінари", "business:education"),
                ("🏢 B2B продажі", "business:b2b"),
                ("➕ Інше", "business:other"),
            ]
        ),
    )


@router.callback_query(F.data.startswith("business:"))
async def set_business(callback, state: FSMContext) -> None:
    business_type = callback.data.split(":", 1)[1]
    await upsert_lead(callback, business_type=business_type)
    await state.update_data(business_type=business_type)
    await state.set_state(LeadFlow.role)
    await callback.message.answer(
        f"{diagnostic_header(2, 'Ваша роль')}\n"
        "Тепер зрозуміємо, з якої позиції ви дивитесь на систему. Це впливає на те, що показувати далі: стратегічну картину, продажі чи операційку.\n\n"
        "Хто ви в цьому бізнесі?",
        reply_markup=grid_keyboard(
            [
                ("👑 Власник / CEO", "role:owner"),
                ("📈 Маркетинг / продажі", "role:growth"),
                ("⚙️ Операційний менеджер", "role:ops"),
                ("🤝 Підрядник / інтегратор", "role:partner"),
            ]
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("role:"))
async def set_role(callback, state: FSMContext) -> None:
    role = callback.data.split(":", 1)[1]
    await upsert_lead(callback, role=role)
    await state.update_data(role=role)
    await state.set_state(LeadFlow.monthly_volume)
    await callback.message.answer(
        f"{diagnostic_header(3, 'Поточний обсяг')}\n"
        "Обсяг показує, яку систему варто будувати: легкий прогрів, повноцінний pipeline або вже контроль статусів і менеджерів.\n\n"
        "Скільки заявок або продажів проходить за місяць?",
        reply_markup=grid_keyboard(
            [
                ("🌱 До 30 / міс", "volume:low"),
                ("🔥 30-150 / міс", "volume:mid"),
                ("🚀 150+ / міс", "volume:high"),
                ("🧩 Важко порахувати", "volume:unknown"),
            ]
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("volume:"))
async def set_volume(callback, state: FSMContext) -> None:
    monthly_volume = callback.data.split(":", 1)[1]
    await upsert_lead(callback, monthly_volume=monthly_volume)
    await state.update_data(monthly_volume=monthly_volume)
    await state.set_state(LeadFlow.scale_problem)
    await callback.message.answer(
        f"{diagnostic_header(4, 'Вузьке місце')}\n"
        "Зазвичай масштабування ламається не в рекламі, а між заявкою, прогрівом, відповідями на сумніви і продажем.\n\n"
        "Що зараз найбільше блокує ріст?",
        reply_markup=grid_keyboard(
            [
                ("💸 Ліди не дотискаються", "problem:followup"),
                ("🧯 Підтримка з'їдає час", "problem:support"),
                ("🔥 Немає прогріву", "problem:warmup"),
                ("📊 Немає трекінгу покупок", "problem:tracking"),
            ]
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("problem:"))
async def set_problem(callback, state: FSMContext) -> None:
    problem = callback.data.split(":", 1)[1]
    await upsert_lead(callback, scale_problem=problem)
    await state.update_data(scale_problem=problem)
    await state.set_state(LeadFlow.has_bot)
    await callback.message.answer(
        f"{diagnostic_header(5, 'Поточна система')}\n"
        "Важливий нюанс: якщо бот вже є, не треба робити “ще один бот”. Треба зрозуміти, де просідає логіка: сегментація, FAQ, прогрів, handoff у продажі або трекінг.\n\n"
        "У вас вже є Telegram-бот або CRM-автоматизація?",
        reply_markup=grid_keyboard(
            [
                ("🆕 Немає, треба з нуля", "bot:no"),
                ("🛠 Є, але слабкий", "bot:weak"),
                ("✅ Є нормальна система", "bot:yes"),
            ]
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("bot:"))
async def set_has_bot(callback, state: FSMContext) -> None:
    has_bot = callback.data.split(":", 1)[1]
    await upsert_lead(callback, has_bot=has_bot)
    await state.update_data(has_bot=has_bot)
    await state.set_state(LeadFlow.current_tools)
    if has_bot == "yes":
        question = (
            f"{diagnostic_header(6, 'Карта системи')}\n"
            "Бачу, що база вже є. Тоді важливо не ламати існуючу систему, а знайти місце, де вона просідає: заявки, прогрів, FAQ, продажі або трекінг.\n\n"
            "Що зараз є основою процесу?"
        )
    else:
        question = (
            f"{diagnostic_header(6, 'Карта системи')}\n"
            "Тут не шукаємо “ідеальну відповідь”. Треба зрозуміти, як зараз живе клієнтський шлях: де приходить заявка, хто нагадує, де губиться контекст.\n\n"
            "Що найближче до вашої ситуації?"
        )
    await callback.message.answer(
        question,
        reply_markup=grid_keyboard(
            [
                ("💬 Менеджери вручну", "tools:manual_messengers"),
                ("📋 Таблиці / Excel", "tools:sheets"),
                ("🧭 CRM / pipeline", "tools:crm"),
                ("🤖 Простий бот", "tools:bot_basic"),
                ("📲 Direct / Telegram", "tools:ads_direct"),
                ("🌐 Сайт / форми", "tools:site_forms"),
                ("💳 Оплати / статуси", "tools:payments_tracking"),
                ("🧩 Усього потроху", "tools:mixed"),
                ("✍️ Написати своїми словами", "tools:custom"),
            ],
            columns=2,
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("tools:"))
async def set_tools_choice(callback, state: FSMContext) -> None:
    tools_choice = callback.data.split(":", 1)[1]
    if tools_choice == "custom":
        await callback.message.answer(
            "Добре. Напишіть одним повідомленням, як зараз у вас рухається клієнт: звідки приходить заявка, де ведеться переписка, хто нагадує і де фіксується статус.\n\n"
            "Можна коротко, людською мовою."
        )
        await callback.answer()
        return

    current_tools = tools_choice_label(tools_choice)
    await upsert_lead(callback, current_tools=current_tools)
    await state.update_data(current_tools=current_tools)
    await callback.message.answer(
        "Зафіксував.\n\n"
        f"Поточна основа: {current_tools}.\n\n"
        "Це допоможе не пропонувати абстрактного бота, а зібрати сценарій під реальний процес: сегменти, follow-up, FAQ, прогрів і передачу менеджеру."
    )
    await move_to_urgency(callback, state)
    await callback.answer()


@router.message(LeadFlow.current_tools)
async def set_current_tools(message: Message, state: FSMContext) -> None:
    await upsert_lead(message, current_tools=message.text or "")
    await state.update_data(current_tools=message.text or "")
    await move_to_urgency(message, state)


@router.callback_query(F.data.startswith("urgency:"))
async def set_urgency(callback, state: FSMContext) -> None:
    urgency = callback.data.split(":", 1)[1]
    data = await state.get_data()
    segment = "hot" if urgency in {"now", "soon"} else "nurture"
    await upsert_lead(callback, urgency=urgency, segment=segment, intent="videos_started")
    await state.clear()
    business = business_label(data.get("business_type"))
    problem = problem_insight(data.get("scale_problem"))
    volume = volume_insight(data.get("monthly_volume"))
    await callback.message.answer(
        f"✅ Діагностику завершено, {first_name(callback)}.\n\n"
        f"Ваш маршрут схожий на задачу в {business}: не просто “зробити бота”, а зібрати зрозумілу систему, яка веде людину від першого інтересу до консультації або покупки.\n\n"
        f"{problem}\n"
        f"{volume}\n\n"
        "Далі відкриваю 3 короткі відео. Їх краще дивитись по черзі:\n\n"
        "01 · Де губляться гроші без follow-up\n"
        "02 · Як бот веде людину до рішення\n"
        "03 · Пакет, гарантія, підтримка, вебінари і трекінг",
        reply_markup=keyboard(
            [
                ("▶️ Почати з відео 1", "video:1"),
                ("📞 Одразу на консультацію", "consultation:start"),
                ("💬 Часті питання", "faq:start"),
            ]
        ),
    )
    await schedule_followups(callback, ["diagnosis_2h", "nurture_3d"], reset_pending=True)
    await callback.answer()


@router.callback_query(F.data.startswith("video:"))
async def video(callback) -> None:
    number = int(callback.data.split(":", 1)[1])
    await upsert_lead(callback, intent=f"video_{number}_viewed")
    texts = {
        1: (
            "▶️ Відео 1/3 · Де бізнес втрачає гроші\n\n"
            "Проблема часто не в кількості заявок. Гроші губляться після першого контакту: людині не нагадали, не відповіли на сумнів, не показали наступний крок.\n\n"
            "Що має робити система:\n"
            "• ловити інтерес одразу;\n"
            "• м'яко повертати людину;\n"
            "• не давати теплим заявкам зникнути;\n"
            "• передавати в продажі тих, хто реально готовий."
        ),
        2: (
            "▶️ Відео 2/3 · Бот як система, а не автовідповідач\n\n"
            "Професійний бот не просто відповідає. Він поводиться як уважний помічник: запитує потрібне, не тисне, пояснює, пам'ятає контекст і веде до наступного кроку.\n\n"
            "Серце системи:\n"
            "• сегментація бізнесу;\n"
            "• прогрів через відео і вебінари;\n"
            "• FAQ без хаосу в менеджерах;\n"
            "• база контактів у Postgres;\n"
            "• handoff на консультацію."
        ),
        3: (
            "▶️ Відео 3/3 · Що всередині пакета\n\n"
            "Пакет має закривати не тільки запуск, а й довіру після запуску.\n\n"
            "Всередині:\n"
            "• базовий пакет автоматизації;\n"
            "• VIP-консультація;\n"
            "• 7 днів повернення;\n"
            "• техпідтримка;\n"
            "• вебінари і FAQ;\n"
            "• трекінг заявок, покупок і статусів.\n\n"
            "Якщо у вас вже є бот, дивимось не на заміну, а на слабкі місця системи."
        ),
    }
    next_buttons = []
    if number < 3:
        next_buttons.append((f"▶️ Відео {number + 1}", f"video:{number + 1}"))
    next_buttons.extend([("📞 Консультація", "consultation:start"), ("💬 FAQ", "faq:start")])
    await callback.message.answer(texts[number], reply_markup=keyboard(next_buttons))
    if number == 1:
        await schedule_followups(callback, ["video1_20h", "nurture_3d"], reset_pending=True)
    elif number == 2:
        await schedule_followups(callback, ["video2_24h", "nurture_3d"], reset_pending=True)
    else:
        await schedule_followups(callback, ["nurture_3d"], reset_pending=True)
    await callback.answer()


@router.callback_query(F.data == "faq:start")
async def faq(callback) -> None:
    await upsert_lead(callback, intent="faq_viewed")
    await callback.message.answer(
        "💬 Часті питання\n\n"
        "Чи є гарантія?\n"
        "Так. 7 днів повернення, якщо рішення не підходить.\n\n"
        "Що з підтримкою?\n"
        "Допомагаємо після запуску, щоб система не залишилась “мертвою схемою”.\n\n"
        "Чи можна трекати покупки?\n"
        "Так. Можемо бачити заявки, покупки, статуси клієнтів і місця, де люди відвалюються.\n\n"
        "Якщо бот вже є?\n"
        "Не дублюємо його. Шукаємо слабкі місця в follow-up, прогріві, FAQ і передачі в продажі.",
        reply_markup=keyboard([("📞 Вийти на консультацію", "consultation:start")]),
    )
    await schedule_followups(callback, ["faq_36h", "nurture_3d"], reset_pending=True)
    await callback.answer()


@router.callback_query(F.data == "consultation:start")
async def consultation(callback, state: FSMContext) -> None:
    await upsert_lead(callback, intent="phone_requested")
    await state.set_state(LeadFlow.phone)
    await schedule_followups(callback, ["consultation_3h"], reset_pending=True)
    await callback.message.answer(
        "📞 Консультація\n\n"
        "Якщо відчуваєте, що у вас є заявки, але система не дотискає людей до наступного кроку — залиште номер.\n\n"
        "На дзвінку розберемо:\n"
        "• тип бізнесу і сегменти клієнтів;\n"
        "• поточний follow-up;\n"
        "• що вже можна автоматизувати;\n"
        "• який перший крок дасть найбільше користі.\n\n"
        "Можна натиснути кнопку нижче або написати номер вручну.",
        reply_markup=contact_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "followup:stop")
async def stop_followups(callback) -> None:
    await upsert_lead(callback, followup_opt_out=1, intent="followup_opt_out")
    await cancel_pending_followups(callback.from_user.id, reason="opted_out")
    await callback.message.answer(
        "Добре, більше не буду нагадувати.\n\n"
        "Якщо захочете повернутись до діагностики або відео, напишіть /start."
    )
    await callback.answer()


@router.message(LeadFlow.phone)
async def noop_phone(message: Message, state: FSMContext) -> None:
    await collect_phone(message, state)


@router.message(F.contact)
async def collect_contact(message: Message, state: FSMContext) -> None:
    await collect_phone(message, state)


@router.message(F.text.regexp(r"^\\+?[0-9 ()\\-]{7,}$"))
async def collect_phone_text(message: Message, state: FSMContext) -> None:
    await collect_phone(message, state)


async def collect_phone(message: Message, state: FSMContext) -> None:
    phone = message.contact.phone_number if message.contact else (message.text or "").strip()
    await upsert_lead(message, phone=phone, intent="consultation_requested")
    await cancel_pending_followups(message.from_user.id, reason="converted")
    await state.clear()
    sales_line = f"\n\nЯкщо зручніше самому: {settings.sales_phone}" if settings.sales_phone else ""
    await message.answer(
        "✅ Номер збережено. Заявка на консультацію створена.\n\n"
        "Контекст діагностики теж збережений, тому на дзвінку можна буде одразу перейти до суті: бізнес, сегменти клієнтів, follow-up і перший процес для автоматизації."
        f"{sales_line}",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message()
async def fallback(message: Message) -> None:
    if (message.text or "").strip().lower() in {"стоп", "stop", "не нагадувати"}:
        await upsert_lead(message, followup_opt_out=1, intent="followup_opt_out")
        await cancel_pending_followups(message.from_user.id, reason="opted_out")
        await message.answer("Добре, більше не буду нагадувати. Повернутись можна через /start.")
        return
    await upsert_lead(message, notes=message.text or "", intent="free_text")
    await message.answer(
        "Зберіг відповідь.\n\n"
        "Щоб пройти діагностику з початку, натисніть /start. Якщо хочете консультацію, залиште номер телефону."
    )


async def main() -> None:
    await init_db()
    bot = Bot(settings.bot_token)
    dp = Dispatcher()
    dp.include_router(router)
    worker_task = None
    if settings.followup_enabled:
        worker_task = asyncio.create_task(followup_worker(bot))
    try:
        await dp.start_polling(bot)
    finally:
        if worker_task is not None:
            worker_task.cancel()
            with suppress(asyncio.CancelledError):
                await worker_task
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
