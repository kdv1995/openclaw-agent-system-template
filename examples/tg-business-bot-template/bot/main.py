import asyncio
import json
from datetime import datetime, timedelta, timezone
from contextlib import suppress
from aiogram import BaseMiddleware, Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    BotCommand,
)
from typing import Any

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import and_, desc, func, or_, select

from .config import settings
from .db import BriefSubmission, ConversationMessage, FollowUp, Lead, SessionLocal, init_db
from .sendpulse_crm import SendPulseCRMClient


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


class BriefFlow(StatesGroup):
    answer = State()


PROGRESS_TOTAL = 6
MAX_PENDING_FOLLOWUPS = 4

PUBLIC_COMMANDS = [
    BotCommand(command="start", description="Заповнити бриф і отримати відео"),
    BotCommand(command="videos", description="Подивитись коротке відео"),
    BotCommand(command="brief", description="Заповнити бриф перед стратегічною сесією"),
    BotCommand(command="consultation", description="Залишити номер для аудиту"),
    BotCommand(command="stop", description="Вимкнути нагадування"),
    BotCommand(command="help", description="Що вміє цей бот"),
]

BRIEF_TEXT_STEPS = [
    (
        "identity",
        "👤 Хто ви в бізнесі?\n\n"
        "Напишіть вашу роль і що зараз тримається особисто на вас.\n"
        "Приклад: «Я власник клініки, на мені продажі, команда і ключові рішення».",
    ),
    (
        "business",
        "🏢 Який у вас бізнес?\n\n"
        "Напишіть що продаєте, кому допомагаєте і на якому ринку працюєте.\n"
        "Приклад: «Онлайн-школа англійської для дорослих по Україні».",
    ),
    (
        "revenue",
        "💰 Скільки бізнес заробляє зараз?\n\n"
        "Можна написати приблизно. Це потрібно не для оцінки, а щоб зрозуміти масштаб рішення.\n"
        "Приклад: «оборот 300-500 тис. грн/міс» або «середній чек 8000 грн».",
    ),
    (
        "avatar",
        "🎯 Хто ваш ідеальний клієнт?\n\n"
        "Опишіть аватар: хто ця людина, чого вона хоче, чого боїться і чому купує.\n"
        "Приклад: «власник бізнесу 30-45, хоче більше продажів без хаосу в команді».",
    ),
    (
        "customer_pains",
        "🩺 Які болі є у вашого клієнта?\n\n"
        "Напишіть, що його дратує, лякає або заважає довіритись і купити.\n"
        "Приклад: «не довіряє, довго думає, боїться переплатити, не розуміє результат».",
    ),
    (
        "desired_result",
        "🚀 Який стан бізнесу ви хочете відчути після роботи з нами?\n\n"
        "Опишіть не послугу, а відчуття: більше контролю, спокою, швидкості, ясності або свободи від ручної роботи.\n"
        "Приклад: «я бачу всі заявки, команда працює без хаосу, AI-штаб показує слабкі місця, а я не тушу пожежі щодня».",
    ),
    (
        "year_vision",
        "🏁 Ким ви хочете бачити себе і компанію через рік?\n\n"
        "Дайте собі місце пофантазувати: як ви прокидаєтесь, як керуєте, що вже не висить на вас і якою стала команда.\n"
        "Приклад: «я керую через цифри, не живу в операційці, команда сама веде процеси, а компанія росте системно».",
    ),
]

BRIEF_MULTI_STEPS = {
    3: {
        "key": "business_problems",
        "title": "🧩 Де бізнес зараз забирає у вас найбільше енергії?",
        "options": [
            ("sales_chaos", "📉 Продажі нестабільні"),
            ("lost_leads", "📥 Заявки губляться"),
            ("team_chaos", "👥 Команда працює хаотично"),
            ("no_followup", "↩️ Немає системного follow-up"),
            ("low_trust", "🤝 Клієнти питають, але не купують"),
            ("no_ceo_dashboard", "📊 CEO не бачить повної картини"),
            ("manual_work", "⚙️ Забагато ручної роботи"),
            ("no_ai_system", "🧠 Немає AI-штабу / системи управління"),
        ],
    },
}

BRIEF_TOTAL_STEPS = len(BRIEF_TEXT_STEPS) + len(BRIEF_MULTI_STEPS)

LEAD_FIELD_DESCRIPTIONS = [
    ("telegram_id", "Telegram ID користувача"),
    ("username", "нік у Telegram"),
    ("full_name", "ім'я з Telegram"),
    ("phone", "номер для консультації"),
    ("business_type", "тип бізнесу"),
    ("role", "роль людини"),
    ("monthly_volume", "обсяг заявок / продажів"),
    ("scale_problem", "головне вузьке місце"),
    ("has_bot", "чи є бот / CRM-автоматизація"),
    ("current_tools", "поточні інструменти"),
    ("urgency", "терміновість запуску"),
    ("segment", "hot або nurture"),
    ("intent", "останній важливий крок"),
    ("notes", "вільний текст від людини"),
    ("followup_opt_out", "чи вимкнені нагадування"),
    ("last_followup_stage", "останній відправлений follow-up"),
    ("created_at", "коли лід створений"),
    ("updated_at", "коли востаннє оновлений"),
]


FOLLOWUP_STAGES = {
    "diagnosis_2h": {
        "delay": timedelta(hours=2),
        "text": (
            "Коротке нагадування.\n\n"
            "Ви вже пройшли діагностику. Найкраще зараз не відкладати відео 1: там показано, де бізнес зазвичай губить теплі заявки після першого контакту.\n\n"
            "Якщо актуально, продовжіть з відео або одразу залиште номер для аудиту."
        ),
    },
    "brief_started_4h": {
        "delay": timedelta(hours=4),
        "text": (
            "📋 Коротке нагадування про бриф.\n\n"
            "Якщо розбір ще актуальний, краще завершити його зараз: відповіді допоможуть підготувати аналітику по аватару клієнта, болях бізнесу, воронці та першому процесу для автоматизації.\n\n"
            "Після брифа ви отримаєте персональний контекст і коротке відео з наступним кроком до аудиту."
        ),
    },
    "brief_completed_3m": {
        "delay": timedelta(minutes=3),
        "text": (
            "🧭 Щоб не залишати розбір на рівні теорії, пропоную перейти до короткого аудиту.\n\n"
            "Ми вже матимемо ваш бриф, тому на дзвінку можна одразу пройтись по аватару клієнта, головних болях бізнесу, вузьких місцях у заявках і першому сценарію автоматизації.\n\n"
            "Залиште номер — підготуємось по вашому контексту."
        ),
    },
    "brief_completed_20h": {
        "delay": timedelta(hours=20),
        "text": (
            "📌 Ваш бриф уже збережений.\n\n"
            "Якщо ще не перейшли до аудиту, зараз хороший момент: поки контекст свіжий, легше визначити перший процес, який варто автоматизувати."
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
            "Якщо головне питання зараз не “що таке бот”, а “чи окупиться система саме в нашому процесі”, краще розібрати це на короткому аудиті: заявки, сегменти, follow-up і перший процес для автоматизації."
        ),
    },
    "consultation_3h": {
        "delay": timedelta(hours=3),
        "text": (
            "📊 М'яке нагадування про аудит.\n\n"
            "Якщо зручно, залиште номер. На дзвінку не треба буде пояснювати все з нуля: у нас вже буде бриф, контекст бізнесу, болі клієнта і перший напрям для розбору."
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


def brief_text_index(cursor: int) -> int:
    multi_before = sum(1 for position in BRIEF_MULTI_STEPS if position < cursor)
    return cursor - multi_before


def brief_multi_keyboard(step: dict[str, Any], selected: list[str]) -> InlineKeyboardMarkup:
    rows = []
    selected_values = set(selected)
    for option_id, label in step["options"]:
        marker = "✅" if option_id in selected_values or label in selected_values else "⬜"
        rows.append([InlineKeyboardButton(text=f"{marker} {label}", callback_data=f"brief:toggle:{option_id}")])
    rows.append([InlineKeyboardButton(text="→ Далі", callback_data="brief:next")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def brief_progress(cursor: int) -> str:
    done = min(cursor + 1, BRIEF_TOTAL_STEPS)
    return f"🧭 Крок {done}/{BRIEF_TOTAL_STEPS}"


def contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Надіслати номер телефону", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def admin_ids() -> set[int]:
    ids: set[int] = set()
    for raw_id in settings.admin_telegram_ids.replace(";", ",").split(","):
        raw_id = raw_id.strip()
        if raw_id:
            with suppress(ValueError):
                ids.add(int(raw_id))
    return ids


def is_admin_user(user: Any) -> bool:
    user_id = getattr(user, "id", None)
    return isinstance(user_id, int) and user_id in admin_ids()


def persistent_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="📋 Бриф"), KeyboardButton(text="▶️ Відео")],
        [KeyboardButton(text="📊 Аудит")],
        [KeyboardButton(text="🔕 Стоп")],
    ]
    if is_admin:
        rows.append([KeyboardButton(text="📈 Sales dashboard")])
    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        input_field_placeholder="Оберіть дію або напишіть питання",
    )


def followup_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 Бриф", callback_data="brief:start"),
                InlineKeyboardButton(text="▶️ Відео 1", callback_data="video:1"),
            ],
            [
                InlineKeyboardButton(text="📊 Аудит", callback_data="consultation:start"),
            ],
            [InlineKeyboardButton(text="🔕 Не нагадувати", callback_data="followup:stop")],
        ]
    )


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return keyboard(
        [
            ("📋 Заповнити бриф", "brief:start"),
            ("▶️ Персональне відео", "menu:videos"),
            ("📊 Аудит", "consultation:start"),
            ("🔕 Не нагадувати", "followup:stop"),
        ]
    )


def videos_keyboard() -> InlineKeyboardMarkup:
    return keyboard(
        [
            ("▶️ Дивитись відео", "video:1"),
            ("📊 Перейти до аудиту", "consultation:start"),
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


def has_bot_label(value: str | None) -> str:
    labels = {
        "no": "бота/CRM-автоматизації поки немає",
        "weak": "є бот або автоматизація, але логіка слабка",
        "yes": "є нормальна система",
    }
    return labels.get(value or "", value or "")


def lead_status_text(lead: Lead | None) -> str:
    if lead is None:
        return (
            "Поки не бачу вашої діагностики.\n\n"
            "Натисніть /start, і бот за кілька кроків збере контекст: тип бізнесу, обсяг заявок, вузьке місце, поточні інструменти і готовність до запуску."
        )

    rows = [
        ("Бізнес", business_label(lead.business_type) if lead.business_type else None),
        ("Роль", lead.role),
        ("Обсяг", lead.monthly_volume),
        ("Вузьке місце", lead.scale_problem),
        ("Поточна система", lead.current_tools or has_bot_label(lead.has_bot)),
        ("Терміновість", lead.urgency),
        ("Сегмент", lead.segment),
        ("Останній крок", lead.intent),
        ("Follow-up", "вимкнено" if lead.followup_opt_out else "увімкнено"),
    ]
    filled = [f"• {label}: {value}" for label, value in rows if value]
    if not filled:
        filled.append("• Діагностика ще не заповнена")
    return "Ваш поточний статус у боті:\n\n" + "\n".join(filled)


def answer_value(answers: dict[str, Any], key: str) -> str:
    value = answers.get(key)
    if isinstance(value, list):
        return ", ".join(value) if value else "—"
    if value is None or str(value).strip() == "":
        return "—"
    return str(value).strip()


def answer_text(answers: dict[str, Any], *keys: str) -> str:
    values = []
    for key in keys:
        value = answers.get(key)
        if isinstance(value, list):
            values.extend(value)
        elif value:
            values.append(str(value))
    return " ".join(values).lower()


def classify_brief(answers: dict[str, Any]) -> dict[str, str]:
    goal = answer_text(answers, "desired_result", "year_vision")
    pains = answer_text(answers, "business_problems", "customer_pains")
    business = answer_text(answers, "identity", "business", "revenue", "avatar")
    all_text = " ".join([goal, pains, business])

    not_ready_markers = {
        "просто дивлюсь",
        "дивлюсь варіанти",
        "поки дивлюсь",
        "поки вивчаю",
        "не знаю",
        "не точно",
        "колись",
        "пізніше",
        "немає бізнесу",
        "ідея",
        "без бюджету",
    }
    strong_goal_markers = {
        "масштаб",
        "ріст",
        "вирости",
        "збільш",
        "система",
        "автомат",
        "ai",
        "аі",
        "штаб",
        "ceo",
        "продаж",
        "команда",
    }
    pain_markers = {
        "заявк",
        "продаж",
        "оплат",
        "менеджер",
        "direct",
        "директ",
        "telegram",
        "дзвін",
        "губ",
        "довго",
        "повтор",
        "ручн",
        "не куп",
        "хаос",
        "нестаб",
        "контрол",
        "довір",
    }

    has_not_ready = any(marker in all_text for marker in not_ready_markers)
    has_strong_goal = any(marker in goal for marker in strong_goal_markers)
    has_pain = any(marker in pains for marker in pain_markers)
    has_business_context = len(business.strip()) >= 35

    if has_not_ready or not has_business_context or not has_pain:
        return {
            "segment": "nurture",
            "qualification": "Поки не готовий до глибокого аудиту: треба догріти і уточнити контекст.",
        }
    if has_strong_goal:
        return {
            "segment": "hot",
            "qualification": "Готовий до аудиту: є бізнес-контекст, болі і бажаний результат.",
        }
    return {
        "segment": "nurture",
        "qualification": "Є контекст і біль, але бажаний результат поки нечіткий: краще прогріти перед аудитом.",
    }


def format_brief(answers: dict[str, Any], include_internal: bool = False) -> str:
    qualification = answers.get("_qualification")
    lines = [
        "📋 КОРОТКИЙ БІЗНЕС-БРИФ",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        "👤 ХТО ЗВЕРНУВСЯ:",
        answer_value(answers, "identity"),
        "",
        "🏢 БІЗНЕС:",
        answer_value(answers, "business"),
        "",
        "💰 ПОТОЧНІ ЦИФРИ:",
        answer_value(answers, "revenue"),
        "",
        "🧩 БОЛІ БІЗНЕСУ:",
        answer_value(answers, "business_problems"),
        "",
        "🎯 АВАТАР КЛІЄНТА:",
        answer_value(answers, "avatar"),
        "",
        "🩺 БОЛІ КЛІЄНТА:",
        answer_value(answers, "customer_pains"),
        "",
        "🚀 БАЖАНИЙ СТАН ПІСЛЯ РОБОТИ З НАМИ:",
        answer_value(answers, "desired_result"),
        "",
        "🏁 СЕБЕ І КОМПАНІЯ ЧЕРЕЗ РІК:",
        answer_value(answers, "year_vision"),
    ]
    if include_internal:
        lines.extend(["", "🧭 КВАЛІФІКАЦІЯ:", str(qualification or "—")])
    return "\n".join(lines)


def short_value(value: Any, empty: str = "—", limit: int = 42) -> str:
    if value is None or value == "":
        return empty
    text = str(value).replace("\n", " ").strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def lead_line(lead: Lead) -> str:
    name = short_value(lead.full_name or lead.username or lead.telegram_id, limit=26)
    username = f"@{lead.username}" if lead.username else f"id:{lead.telegram_id}"
    status_bits = [
        short_value(lead.segment),
        short_value(lead.intent, limit=24),
        "phone" if lead.phone else "no phone",
    ]
    return (
        f"• {name} ({username})\n"
        f"  {', '.join(status_bits)} · {short_value(lead.business_type)} · {short_value(lead.scale_problem)}"
    )


async def sales_dashboard_text() -> str:
    async with SessionLocal() as session:
        total = await session.scalar(select(func.count(Lead.id)))
        with_phone = await session.scalar(select(func.count(Lead.id)).where(Lead.phone.is_not(None)))
        hot = await session.scalar(select(func.count(Lead.id)).where(Lead.segment == "hot"))
        nurture = await session.scalar(select(func.count(Lead.id)).where(Lead.segment == "nurture"))
        opt_out = await session.scalar(select(func.count(Lead.id)).where(Lead.followup_opt_out == 1))
        consultation = await session.scalar(select(func.count(Lead.id)).where(Lead.intent == "consultation_requested"))

        pending_followups = await session.scalar(
            select(func.count(FollowUp.id)).where(FollowUp.status == "pending")
        )
        sent_followups = await session.scalar(select(func.count(FollowUp.id)).where(FollowUp.status == "sent"))
        failed_followups = await session.scalar(select(func.count(FollowUp.id)).where(FollowUp.status == "failed"))

        recent_result = await session.execute(select(Lead).order_by(Lead.updated_at.desc()).limit(5))
        recent_leads = list(recent_result.scalars())

    recent_block = "\n".join(lead_line(lead) for lead in recent_leads) or "• Поки немає лідів"
    fields = "\n".join(f"• {name} — {description}" for name, description in LEAD_FIELD_DESCRIPTIONS)
    return (
        "📈 Sales dashboard\n\n"
        "Воронка:\n"
        f"• Всього лідів: {total or 0}\n"
        f"• Hot: {hot or 0}\n"
        f"• Nurture: {nurture or 0}\n"
        f"• Залишили телефон: {with_phone or 0}\n"
        f"• Consultation requested: {consultation or 0}\n"
        f"• Вимкнули follow-up: {opt_out or 0}\n\n"
        "Follow-up:\n"
        f"• Pending: {pending_followups or 0}\n"
        f"• Sent: {sent_followups or 0}\n"
        f"• Failed: {failed_followups or 0}\n\n"
        "Останні ліди:\n"
        f"{recent_block}\n\n"
        "Поля в базі leads:\n"
        f"{fields}"
    )


async def send_sales_dashboard(message: Message) -> None:
    if not is_admin_user(message.from_user):
        await message.answer("Ця команда доступна тільки адміну.")
        return
    await message.answer(await sales_dashboard_text(), reply_markup=persistent_menu_keyboard(is_admin=True))


class ManagerMessageRequest(BaseModel):
    text: str = Field(min_length=1, max_length=3900)
    sent_by: str = Field(default="crm", max_length=255)


def require_crm_api_key(x_crm_api_key: str | None) -> None:
    if settings.crm_api_key and x_crm_api_key != settings.crm_api_key:
        raise HTTPException(status_code=401, detail="Invalid CRM API key")


def lead_to_dict(lead: Lead) -> dict[str, Any]:
    return {
        "telegram_id": lead.telegram_id,
        "username": lead.username,
        "full_name": lead.full_name,
        "phone": lead.phone,
        "business_type": lead.business_type,
        "role": lead.role,
        "monthly_volume": lead.monthly_volume,
        "scale_problem": lead.scale_problem,
        "has_bot": lead.has_bot,
        "current_tools": lead.current_tools,
        "urgency": lead.urgency,
        "segment": lead.segment,
        "intent": lead.intent,
        "followup_opt_out": bool(lead.followup_opt_out),
        "last_followup_stage": lead.last_followup_stage,
        "sendpulse_contact_id": lead.sendpulse_contact_id,
        "sendpulse_deal_id": lead.sendpulse_deal_id,
        "sendpulse_sync_status": lead.sendpulse_sync_status,
        "sendpulse_sync_error": lead.sendpulse_sync_error,
        "sendpulse_synced_at": lead.sendpulse_synced_at.isoformat() if lead.sendpulse_synced_at else None,
        "created_at": lead.created_at.isoformat() if lead.created_at else None,
        "updated_at": lead.updated_at.isoformat() if lead.updated_at else None,
    }


def conversation_message_to_dict(message: ConversationMessage) -> dict[str, Any]:
    return {
        "id": message.id,
        "telegram_id": message.telegram_id,
        "username": message.username,
        "full_name": message.full_name,
        "direction": message.direction,
        "message_type": message.message_type,
        "text": message.text,
        "payload": json.loads(message.payload_json or "{}"),
        "source": message.source,
        "sent_by": message.sent_by,
        "telegram_message_id": message.telegram_message_id,
        "reply_to_message_id": message.reply_to_message_id,
        "created_at": message.created_at.isoformat() if message.created_at else None,
    }


def create_crm_app(bot: Bot) -> FastAPI:
    app = FastAPI(title="TG Business Bot CRM API")
    app.state.bot = bot

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/crm/leads")
    async def crm_leads(
        limit: int = Query(default=50, ge=1, le=200),
        offset: int = Query(default=0, ge=0),
        x_crm_api_key: str | None = Header(default=None),
    ) -> dict[str, Any]:
        require_crm_api_key(x_crm_api_key)
        async with SessionLocal() as session:
            result = await session.execute(select(Lead).order_by(desc(Lead.updated_at)).offset(offset).limit(limit))
            leads = [lead_to_dict(lead) for lead in result.scalars()]
        return {"items": leads, "limit": limit, "offset": offset}

    @app.get("/crm/leads/{telegram_id}/messages")
    async def crm_messages(
        telegram_id: int,
        limit: int = Query(default=100, ge=1, le=500),
        before_id: int | None = Query(default=None, ge=1),
        x_crm_api_key: str | None = Header(default=None),
    ) -> dict[str, Any]:
        require_crm_api_key(x_crm_api_key)
        query = select(ConversationMessage).where(ConversationMessage.telegram_id == telegram_id)
        if before_id is not None:
            query = query.where(ConversationMessage.id < before_id)
        query = query.order_by(desc(ConversationMessage.id)).limit(limit)
        async with SessionLocal() as session:
            result = await session.execute(query)
            messages = [conversation_message_to_dict(item) for item in reversed(result.scalars().all())]
        return {"items": messages, "limit": limit}

    @app.post("/crm/leads/{telegram_id}/messages")
    async def crm_send_message(
        telegram_id: int,
        request: ManagerMessageRequest,
        x_crm_api_key: str | None = Header(default=None),
    ) -> dict[str, Any]:
        require_crm_api_key(x_crm_api_key)
        sent = await app.state.bot.send_message(chat_id=telegram_id, text=request.text)
        await log_conversation_message(
            telegram_id=telegram_id,
            direction="outbound",
            message_type="text",
            text=request.text,
            payload={"via": "crm_api"},
            source="crm_api",
            sent_by=request.sent_by,
            telegram_message_id=sent.message_id,
        )
        return {"ok": True, "telegram_message_id": sent.message_id}

    return app


async def run_crm_api(bot: Bot) -> None:
    config = uvicorn.Config(
        create_crm_app(bot),
        host=settings.crm_api_host,
        port=settings.crm_api_port,
        log_level="warning",
    )
    server = uvicorn.Server(config)
    await server.serve()


async def send_start_flow(event: Any, target: Any, state: FSMContext) -> None:
    await start_brief_flow(event, target, state)


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


async def upsert_lead(event: Any, **fields: Any) -> None:
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


def sendpulse_ready() -> bool:
    return bool(
        settings.sendpulse_crm_enabled
        and settings.sendpulse_api_key
        and parse_optional_int(settings.sendpulse_responsible_id)
        and parse_optional_int(settings.sendpulse_pipeline_id)
        and parse_optional_int(settings.sendpulse_step_id)
    )


def parse_optional_int(value: Any) -> int | None:
    with suppress(TypeError, ValueError):
        return int(str(value).strip())
    return None


def split_full_name(full_name: str | None, fallback: str) -> tuple[str, str]:
    parts = (full_name or "").strip().split(maxsplit=1)
    if not parts:
        return fallback, ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def sendpulse_note_text(lead: Lead) -> str:
    lines = [
        "Telegram business bot lead",
        f"Telegram ID: {lead.telegram_id}",
        f"Username: @{lead.username}" if lead.username else None,
        f"Phone: {lead.phone}" if lead.phone else None,
        f"Segment: {lead.segment}" if lead.segment else None,
        f"Intent: {lead.intent}" if lead.intent else None,
        f"Business: {lead.business_type}" if lead.business_type else None,
        f"Monthly volume: {lead.monthly_volume}" if lead.monthly_volume else None,
        f"Problem: {lead.scale_problem}" if lead.scale_problem else None,
        f"Desired/current tools: {lead.current_tools}" if lead.current_tools else None,
        f"Vision/urgency: {lead.urgency}" if lead.urgency else None,
        "",
        lead.notes,
    ]
    return "\n".join(line for line in lines if line)


async def sync_lead_to_sendpulse(telegram_id: int) -> None:
    if not sendpulse_ready():
        return
    async with SessionLocal() as session:
        result = await session.execute(select(Lead).where(Lead.telegram_id == telegram_id))
        lead = result.scalar_one_or_none()
        if lead is None or not lead.phone:
            return
        lead.sendpulse_sync_status = "pending"
        lead.sendpulse_sync_error = None
        await session.commit()

    client = SendPulseCRMClient(settings.sendpulse_api_key)
    responsible_id = parse_optional_int(settings.sendpulse_responsible_id)
    pipeline_id = parse_optional_int(settings.sendpulse_pipeline_id)
    step_id = parse_optional_int(settings.sendpulse_step_id)
    if responsible_id is None or pipeline_id is None or step_id is None:
        return
    try:
        existing_contact = await client.find_contact_by_phone(lead.phone)
        if existing_contact:
            contact_id = existing_contact["id"]
        else:
            fallback_name = lead.username or str(lead.telegram_id)
            first, last = split_full_name(lead.full_name, fallback_name)
            contact = await client.create_contact(
                responsible_id=responsible_id,
                first_name=first,
                last_name=last,
                external_contact_id=f"telegram:{lead.telegram_id}",
            )
            contact_id = contact["id"]
            await client.add_phone(contact_id, lead.phone)

        deal_name = f"Telegram audit: {lead.full_name or lead.username or lead.telegram_id}"
        deal = await client.create_deal(
            pipeline_id=pipeline_id,
            step_id=step_id,
            responsible_id=responsible_id,
            contact_id=contact_id,
            name=deal_name,
            price=settings.sendpulse_deal_price,
            currency=settings.sendpulse_deal_currency,
        )
        note = sendpulse_note_text(lead)
        await client.add_contact_note(contact_id, note)
        await client.add_deal_note(deal["id"], note)
    except Exception as exc:
        async with SessionLocal() as session:
            result = await session.execute(select(Lead).where(Lead.telegram_id == telegram_id))
            lead = result.scalar_one_or_none()
            if lead is not None:
                lead.sendpulse_sync_status = "failed"
                lead.sendpulse_sync_error = str(exc)[:2000]
            await session.commit()
        return

    async with SessionLocal() as session:
        result = await session.execute(select(Lead).where(Lead.telegram_id == telegram_id))
        lead = result.scalar_one_or_none()
        if lead is not None:
            lead.sendpulse_contact_id = contact_id
            lead.sendpulse_deal_id = deal["id"]
            lead.sendpulse_sync_status = "synced"
            lead.sendpulse_sync_error = None
            lead.sendpulse_synced_at = datetime.now(timezone.utc)
        await session.commit()


def message_payload(message: Message) -> dict[str, Any]:
    payload: dict[str, Any] = {"content_type": str(message.content_type)}
    if message.contact:
        payload["contact"] = {
            "phone_number": message.contact.phone_number,
            "first_name": message.contact.first_name,
            "last_name": message.contact.last_name,
            "user_id": message.contact.user_id,
        }
    if message.reply_to_message:
        payload["reply_to_message_id"] = message.reply_to_message.message_id
    return payload


async def log_conversation_message(
    *,
    telegram_id: int,
    direction: str,
    text: str | None,
    username: str | None = None,
    full_name: str | None = None,
    message_type: str = "text",
    payload: dict[str, Any] | None = None,
    source: str = "telegram",
    sent_by: str | None = None,
    telegram_message_id: int | None = None,
    reply_to_message_id: int | None = None,
) -> None:
    async with SessionLocal() as session:
        session.add(
            ConversationMessage(
                telegram_id=telegram_id,
                username=username,
                full_name=full_name,
                direction=direction,
                message_type=message_type,
                text=text,
                payload_json=json.dumps(payload or {}, ensure_ascii=False),
                source=source,
                sent_by=sent_by,
                telegram_message_id=telegram_message_id,
                reply_to_message_id=reply_to_message_id,
            )
        )
        await session.commit()


async def log_inbound_message(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    await upsert_lead(message)
    await log_conversation_message(
        telegram_id=user.id,
        username=user.username,
        full_name=user.full_name,
        direction="inbound",
        message_type=str(message.content_type),
        text=message.text or message.caption,
        payload=message_payload(message),
        telegram_message_id=message.message_id,
        reply_to_message_id=message.reply_to_message.message_id if message.reply_to_message else None,
    )


async def log_inbound_callback(callback: CallbackQuery) -> None:
    user = callback.from_user
    payload = {
        "callback_data": callback.data,
        "message_id": callback.message.message_id if callback.message else None,
    }
    await upsert_lead(callback)
    await log_conversation_message(
        telegram_id=user.id,
        username=user.username,
        full_name=user.full_name,
        direction="inbound",
        message_type="callback",
        text=callback.data,
        payload=payload,
        telegram_message_id=payload["message_id"],
    )


class ConversationLogMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            await log_inbound_message(event)
        elif isinstance(event, CallbackQuery):
            await log_inbound_callback(event)
        return await handler(event, data)


async def send_brief_step(target: Message, state: FSMContext) -> None:
    data = await state.get_data()
    cursor = int(data.get("brief_cursor", 0))
    if cursor >= BRIEF_TOTAL_STEPS:
        await finish_brief(target, state)
        return

    if cursor in BRIEF_MULTI_STEPS:
        step = BRIEF_MULTI_STEPS[cursor]
        answers = data.get("brief_answers", {})
        selected = answers.get(step["key"], [])
        await target.answer(
            f"{brief_progress(cursor)}\n{step['title']}\n\n"
            "Натисніть один або кілька варіантів. Потім натисніть «→ Далі».",
            reply_markup=brief_multi_keyboard(step, selected),
        )
        return

    key, question = BRIEF_TEXT_STEPS[brief_text_index(cursor)]
    await target.answer(f"{brief_progress(cursor)}\n{question}")


async def start_brief_flow(event: Any, target: Message, state: FSMContext) -> None:
    await upsert_lead(event, intent="brief_started")
    await state.set_state(BriefFlow.answer)
    await state.set_data({"brief_cursor": 0, "brief_answers": {}})
    await schedule_followups(event, ["brief_started_4h"], reset_pending=True)
    name = first_name(event)
    await target.answer(
        f"Вітаю, {name}.\n\n"
        "Дякуємо, що звернулися. Якщо бізнес росте, але частина процесів тримається на вас особисто — це виснажує і заважає бачити картину тверезо.\n\n"
        "Ми не починаємо з продажу рішення. Спочатку допомагаємо побачити слабкі місця: де губляться гроші, увага клієнта, контроль команди і ваша енергія як CEO.\n\n"
        "Після цього вже можна підібрати рішення: AI-штаб і систему управління, яка знімає ручну роботу, показує цифри й дає керівнику більше контролю.\n\n"
        "🧭 Спочатку короткий бриф: 8 обов'язкових кроків.\n"
        "Він допоможе вам чесно побачити поточну точку, слабкі сторони, бажаний стан себе як керівника і картину компанії через рік.\n\n"
        "✍️ Пишіть відповідь внизу, у полі «Повідомлення».\n\n"
        "Відповідайте коротко: 1 речення або список. У кожному питанні буде приклад.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await send_brief_step(target, state)


async def finish_brief(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    answers = data.get("brief_answers", {})
    qualification = classify_brief(answers)
    answers["_qualification"] = qualification["qualification"]
    text = format_brief(answers)
    internal_text = format_brief(answers, include_internal=True)
    user = message.from_user
    async with SessionLocal() as session:
        session.add(
            BriefSubmission(
                telegram_id=user.id,
                username=user.username,
                full_name=user.full_name,
                data_json=json.dumps(answers, ensure_ascii=False),
                formatted_text=internal_text,
            )
        )
        await session.commit()
    segment = qualification["segment"]
    await upsert_lead(
        message,
        business_type=answer_value(answers, "business"),
        monthly_volume=answer_value(answers, "revenue"),
        current_tools=answer_value(answers, "desired_result"),
        scale_problem=answer_value(answers, "business_problems"),
        urgency=answer_value(answers, "year_vision"),
        segment=segment,
        intent="brief_completed",
        notes=internal_text,
    )
    await state.clear()
    await message.answer(
        "✅ Бриф збережено.\n\n"
        "Нижче коротко зібрав ваші відповіді. По них уже видно не тільки бізнес, а й вашу особисту точку як керівника: що тримається на вас, що виснажує, як ви хочете себе відчувати через рік і що треба розібрати на аудиті.",
        reply_markup=persistent_menu_keyboard(is_admin_user(message.from_user)),
    )
    for start in range(0, len(text), 3900):
        await message.answer(text[start : start + 3900])
    if segment == "hot":
        await message.answer(
            "📊 Наступний крок — аудит.\n\n"
            "На аудиті не будемо продавати “з кінця”. Спочатку розберемо вашу поточну точку, слабкі місця бізнесу, болі клієнта, бажаний стан керівника через рік і перший процес, який варто передати AI-штабу.",
            reply_markup=keyboard([("📊 Перейти до аудиту", "consultation:start"), ("▶️ Спочатку відео", "video:1")]),
        )
    else:
        await message.answer(
            "▶️ Наступний крок — коротке відео перед аудитом.\n\n"
            "Воно допоможе точніше побачити, де бізнес втрачає заявки, контроль, довіру клієнта або вашу енергію як керівника. Після цього легше зрозуміти, яким має бути наступний рівень бізнесу і ваша роль у ньому.",
            reply_markup=keyboard([("▶️ Дивитись відео", "video:1")]),
        )
        await schedule_followups(message, ["brief_completed_20h", "nurture_3d"], reset_pending=True)
        return
    await message.answer(
        "Якщо після аудиту буде актуально — зможемо говорити вже не загально, а по вашій реальній картині: роль CEO зараз, бажаний стан через рік, бізнес, клієнт, болі й перший AI-процес.",
    )
    await schedule_followups(message, ["brief_completed_3m", "brief_completed_20h", "nurture_3d"], reset_pending=True)


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


async def send_videos_menu(message: Message) -> None:
    await upsert_lead(message, intent="videos_menu_opened")
    await message.answer(
        "▶️ Коротке відео перед аудитом\n\n"
        "Покажемо головну ідею: як бізнес втрачає теплі заявки після першого інтересу, і як автоматизація може довести людину до рішення без тиску.\n\n"
        "Після відео логічний наступний крок — залишити номер для персонального аудиту.",
        reply_markup=videos_keyboard(),
    )


async def send_faq(message: Message, intent: str = "faq_command_viewed") -> None:
    await upsert_lead(message, intent=intent)
    await message.answer(
        "💬 Часті питання\n\n"
        "Чи є гарантія?\n"
        "Так. 7 днів повернення, якщо рішення не підходить.\n\n"
        "Що з підтримкою?\n"
        "Допомагаємо після запуску, щоб система не залишилась “мертвою схемою”.\n\n"
        "Чи можна трекати покупки?\n"
        "Так. Можемо бачити заявки, покупки, статуси клієнтів і місця, де люди відвалюються.\n\n"
        "Якщо бот вже є?\n"
        "Не дублюємо його. Шукаємо слабкі місця в follow-up, прогріві, FAQ і передачі в продажі.",
        reply_markup=keyboard([("📊 Перейти до аудиту", "consultation:start"), ("▶️ Подивитись відео", "menu:videos")]),
    )


async def request_consultation(message: Message, state: FSMContext) -> None:
    lead = await get_lead_by_event(message)
    if lead is not None and lead.segment == "nurture":
        await upsert_lead(message, intent="nurture_consultation_blocked")
        await message.answer(
            "Щоб аудит був предметним, спочатку краще подивитись коротке відео або уточнити бриф.\n\n"
            "Так ми зберемо більше контексту і не будемо витрачати ваш час на загальні питання.",
            reply_markup=keyboard([("▶️ Дивитись відео", "video:1"), ("📋 Уточнити бриф", "brief:start")]),
        )
        return
    await upsert_lead(message, intent="phone_requested")
    await state.set_state(LeadFlow.phone)
    await schedule_followups(message, ["consultation_3h"], reset_pending=True)
    sales_line = f"\n\nАбо напишіть/зателефонуйте напряму: {settings.sales_phone}" if settings.sales_phone else ""
    await message.answer(
        "📊 Аудит бізнесу\n\n"
        "Залиште номер телефону. На дзвінку розберемо ваш бриф: хто ви як керівник, що тримається на вас, бізнес-модель, цифри, аватар клієнта, його болі, поточні слабкі місця і як ви хочете відчувати себе в бізнесі через рік.\n\n"
        "🧭 Ціль аудиту — не продати готове рішення, а показати конкретику: що зараз блокує ріст, який процес забирає найбільше енергії і як AI-штаб може допомогти CEO перейти з ручного контролю в системне управління.\n\n"
        "Можна натиснути кнопку нижче або написати номер вручну."
        f"{sales_line}",
        reply_markup=contact_keyboard(),
    )


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await start_brief_flow(message, message, state)


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    admin_line = "\n/sales — адмінський sales dashboard" if is_admin_user(message.from_user) else ""
    await message.answer(
        "Я допомагаю швидко зрозуміти, де бізнес втрачає заявки між першим інтересом і продажем.\n\n"
        "Корисні команди:\n"
        "/start — заповнити бриф і перейти до відео\n"
        "/brief — заповнити бриф перед стратегічною сесією\n"
        "/videos — отримати коротке відео\n"
        "/consultation — залишити номер для аудиту\n"
        f"/stop — вимкнути нагадування{admin_line}",
        reply_markup=persistent_menu_keyboard(is_admin_user(message.from_user)),
    )
    await message.answer("Також можна обрати дію тут:", reply_markup=main_menu_keyboard())


@router.message(Command("menu"))
async def menu_command(message: Message) -> None:
    await message.answer(
        "Головне меню.\n\n"
        "Можна заповнити бриф, повернутися до відео або залишити номер для аудиту.",
        reply_markup=persistent_menu_keyboard(is_admin_user(message.from_user)),
    )
    await message.answer(
        "Швидкий вибір:",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("videos"))
async def videos_command(message: Message) -> None:
    await send_videos_menu(message)


@router.message(Command("faq"))
async def faq_command(message: Message) -> None:
    await send_faq(message)


@router.message(Command("consultation"))
async def consultation_command(message: Message, state: FSMContext) -> None:
    await request_consultation(message, state)


@router.message(Command("brief"))
async def brief_command(message: Message, state: FSMContext) -> None:
    await start_brief_flow(message, message, state)


@router.message(Command("status"))
async def status_command(message: Message) -> None:
    lead = await get_lead_by_event(message)
    await message.answer(lead_status_text(lead), reply_markup=main_menu_keyboard())


@router.message(Command("stop"))
async def stop_command(message: Message, state: FSMContext) -> None:
    await upsert_lead(message, followup_opt_out=1, intent="followup_opt_out")
    await cancel_pending_followups(message.from_user.id, reason="opted_out")
    await state.clear()
    await message.answer(
        "Добре, більше не буду нагадувати.\n\n"
        "Повернутись до брифа можна через /start або /brief.",
        reply_markup=persistent_menu_keyboard(is_admin_user(message.from_user)),
    )


@router.message(Command("sales"))
async def sales_command(message: Message) -> None:
    await send_sales_dashboard(message)


@router.message(F.text == "🧭 Діагностика")
async def diagnosis_button(message: Message, state: FSMContext) -> None:
    await start_brief_flow(message, message, state)


@router.message(F.text == "▶️ Відео")
async def videos_button(message: Message) -> None:
    await send_videos_menu(message)


@router.message(F.text == "💬 FAQ")
async def faq_button(message: Message, state: FSMContext) -> None:
    await start_brief_flow(message, message, state)


@router.message(F.text == "📞 Консультація")
async def consultation_button(message: Message, state: FSMContext) -> None:
    await request_consultation(message, state)


@router.message(F.text == "📊 Аудит")
async def audit_button(message: Message, state: FSMContext) -> None:
    await request_consultation(message, state)


@router.message(F.text == "📊 Мій статус")
async def status_button(message: Message, state: FSMContext) -> None:
    await start_brief_flow(message, message, state)


@router.message(F.text == "🔕 Стоп")
async def stop_button(message: Message, state: FSMContext) -> None:
    await stop_command(message, state)


@router.message(F.text == "📈 Sales dashboard")
async def sales_dashboard_button(message: Message) -> None:
    await send_sales_dashboard(message)


@router.message(F.text == "📋 Бриф")
async def brief_button(message: Message, state: FSMContext) -> None:
    await start_brief_flow(message, message, state)


@router.callback_query(F.data == "brief:start")
async def brief_start_callback(callback, state: FSMContext) -> None:
    await start_brief_flow(callback, callback.message, state)
    await callback.answer()


@router.callback_query(F.data == "menu:diagnosis")
async def menu_diagnosis(callback, state: FSMContext) -> None:
    await send_start_flow(callback, callback.message, state)
    await callback.answer()


@router.callback_query(F.data == "menu:videos")
async def menu_videos(callback) -> None:
    await upsert_lead(callback, intent="videos_menu_opened")
    await callback.message.answer(
        "Оберіть відео, з якого хочете продовжити.",
        reply_markup=videos_keyboard(),
    )
    await callback.answer()


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
    next_step_text = (
        "→ Далі відкриваю коротке відео перед аудитом."
        if segment == "hot"
        else "→ Далі відкриваю коротке відео, щоб краще зрозуміти наступний крок."
    )
    next_step_keyboard = (
        keyboard([("▶️ Дивитись відео", "video:1"), ("📊 Одразу на аудит", "consultation:start")])
        if segment == "hot"
        else keyboard([("▶️ Дивитись відео", "video:1")])
    )
    await callback.message.answer(
        f"✅ Діагностику завершено, {first_name(callback)}.\n\n"
        f"Ваш маршрут схожий на задачу в {business}: не просто “зробити бота”, а зібрати зрозумілу систему, яка веде людину від першого інтересу до консультації, аудиту або покупки.\n\n"
        f"{problem}\n"
        f"{volume}\n\n"
        f"{next_step_text}\n\n"
        "У ньому покажемо, як бізнес втрачає теплі заявки після першого інтересу і як система може довести людину до рішення без тиску.",
        reply_markup=next_step_keyboard,
    )
    await schedule_followups(callback, ["diagnosis_2h", "nurture_3d"], reset_pending=True)
    await callback.answer()


@router.callback_query(F.data.startswith("video:"))
async def video(callback) -> None:
    number = int(callback.data.split(":", 1)[1])
    lead = await get_lead_by_event(callback)
    await upsert_lead(callback, intent="sales_video_viewed")
    texts = {
        1: (
            "▶️ Коротке відео · Як довести людину до рішення\n\n"
            "Проблема часто не в кількості заявок. Гроші губляться після першого інтересу: людині не нагадали, не відповіли на сумнів, не показали наступний крок або занадто пізно передали в продажі.\n\n"
            "🧭 Що має робити система:\n"
            "• фіксувати контекст людини з перших відповідей;\n"
            "• показувати релевантне повідомлення під її ситуацію;\n"
            "• м'яко вести до наступного кроку без тиску;\n"
            "• передавати менеджеру вже підготовлений діалог.\n\n"
            "📌 На аудиті можна швидко визначити перший сценарій: де саме ваш бізнес зараз втрачає заявки і що автоматизувати в першу чергу."
        ),
    }
    text = texts.get(number, texts[1])
    if lead is not None and lead.segment == "nurture":
        await callback.message.answer(
            text,
            reply_markup=keyboard([("📋 Уточнити бриф", "brief:start")]),
        )
        await schedule_followups(callback, ["nurture_3d"], reset_pending=True)
        await callback.answer()
        return
    await callback.message.answer(
        text,
        reply_markup=keyboard([("📊 Перейти до аудиту", "consultation:start")]),
    )
    await schedule_followups(callback, ["brief_completed_3m", "nurture_3d"], reset_pending=True)
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
        reply_markup=keyboard([("📊 Перейти до аудиту", "consultation:start")]),
    )
    await schedule_followups(callback, ["faq_36h", "nurture_3d"], reset_pending=True)
    await callback.answer()


@router.callback_query(F.data == "consultation:start")
async def consultation(callback, state: FSMContext) -> None:
    lead = await get_lead_by_event(callback)
    if lead is not None and lead.segment == "nurture":
        await upsert_lead(callback, intent="nurture_consultation_blocked")
        await callback.message.answer(
            "Щоб аудит був предметним, спочатку краще подивитись коротке відео або уточнити бриф.\n\n"
            "Так ми зберемо більше контексту і не будемо витрачати ваш час на загальні питання.",
            reply_markup=keyboard([("▶️ Дивитись відео", "video:1"), ("📋 Уточнити бриф", "brief:start")]),
        )
        await callback.answer()
        return
    await upsert_lead(callback, intent="phone_requested")
    await state.set_state(LeadFlow.phone)
    await schedule_followups(callback, ["consultation_3h"], reset_pending=True)
    sales_line = f"\n\nАбо напишіть/зателефонуйте напряму: {settings.sales_phone}" if settings.sales_phone else ""
    await callback.message.answer(
        "📊 Аудит бізнесу\n\n"
        "Якщо у вас є заявки, але бізнес все одно забирає забагато особистої енергії, контролю і ручних рішень — залиште номер.\n\n"
        "На дзвінку розберемо:\n"
        "• хто ви як керівник і що зараз тримається на вас;\n"
        "• аватар клієнта і його реальні болі;\n"
        "• що блокує продажі, команду, контроль або вашу енергію;\n"
        "• ким ви хочете бути в цій компанії через рік;\n"
        "• який перший процес варто передати AI-штабу.\n\n"
        "Можна натиснути кнопку нижче або написати номер вручну."
        f"{sales_line}",
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


@router.callback_query(F.data == "brief:cancel")
async def brief_cancel(callback, state: FSMContext) -> None:
    await state.clear()
    await upsert_lead(callback, intent="brief_cancelled")
    await callback.message.answer(
        "Бриф скасовано. Повернутись можна через /brief.",
        reply_markup=persistent_menu_keyboard(is_admin_user(callback.from_user)),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("brief:toggle:"))
async def brief_toggle(callback, state: FSMContext) -> None:
    option_id = callback.data.rsplit(":", 1)[1]
    data = await state.get_data()
    cursor = int(data.get("brief_cursor", 0))
    step = BRIEF_MULTI_STEPS.get(cursor)
    if step is None:
        await callback.answer()
        return
    option_labels = dict(step["options"])
    answers = data.get("brief_answers", {})
    selected = list(answers.get(step["key"], []))
    label = option_labels.get(option_id)
    if label is None:
        await callback.answer()
        return
    if label in selected:
        selected.remove(label)
    else:
        selected.append(label)
    answers[step["key"]] = selected
    await state.update_data(brief_answers=answers)
    await callback.message.edit_reply_markup(reply_markup=brief_multi_keyboard(step, selected))
    await callback.answer()


@router.callback_query(F.data == "brief:next")
async def brief_next(callback, state: FSMContext) -> None:
    data = await state.get_data()
    cursor = int(data.get("brief_cursor", 0))
    step = BRIEF_MULTI_STEPS.get(cursor)
    if step is not None:
        selected = data.get("brief_answers", {}).get(step["key"], [])
        if not selected:
            await callback.answer("Оберіть хоча б один варіант, щоб продовжити.", show_alert=True)
            return
    await state.update_data(brief_cursor=cursor + 1)
    await send_brief_step(callback.message, state)
    await callback.answer()


@router.message(BriefFlow.answer)
async def collect_brief_answer(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if text.lower() in {"стоп", "stop", "отмена", "скасувати", "cancel"}:
        await state.clear()
        await upsert_lead(message, intent="brief_cancelled")
        await message.answer("Бриф скасовано. Повернутись можна через /brief.")
        return
    if text.lower() in {"", "нет", "ні", "-", "—", "пропустить", "пропустити", "skip"}:
        await message.answer("Цей крок обов'язковий. Напишіть коротко, хоча б одним реченням.")
        return
    data = await state.get_data()
    cursor = int(data.get("brief_cursor", 0))
    if cursor in BRIEF_MULTI_STEPS:
        await message.answer("Тут потрібно вибрати варіант кнопками і натиснути «→ Далі».")
        return
    answers = data.get("brief_answers", {})
    key, _ = BRIEF_TEXT_STEPS[brief_text_index(cursor)]
    answers[key] = text
    await state.update_data(brief_cursor=cursor + 1, brief_answers=answers)
    await send_brief_step(message, state)


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
    asyncio.create_task(sync_lead_to_sendpulse(message.from_user.id))
    await state.clear()
    sales_line = f"\n\nЯкщо зручніше самому: {settings.sales_phone}" if settings.sales_phone else ""
    await message.answer(
        "✅ Номер збережено. Заявка на аудит створена.\n\n"
        "Контекст брифа теж збережений, тому на дзвінку можна буде одразу перейти до суті: бізнес, аватар клієнта, болі, цілі й перший процес для AI-штабу."
        f"{sales_line}",
        reply_markup=persistent_menu_keyboard(is_admin_user(message.from_user)),
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
        "Щоб пройти бриф з початку, натисніть “📋 Бриф”. Якщо хочете аудит, натисніть “📊 Аудит”.",
        reply_markup=persistent_menu_keyboard(is_admin_user(message.from_user)),
    )


async def main() -> None:
    await init_db()
    bot = Bot(settings.bot_token)
    await bot.set_my_commands(PUBLIC_COMMANDS)
    dp = Dispatcher()
    conversation_log_middleware = ConversationLogMiddleware()
    dp.message.outer_middleware(conversation_log_middleware)
    dp.callback_query.outer_middleware(conversation_log_middleware)
    dp.include_router(router)
    worker_task = None
    api_task = None
    if settings.followup_enabled:
        worker_task = asyncio.create_task(followup_worker(bot))
    if settings.crm_api_enabled:
        api_task = asyncio.create_task(run_crm_api(bot))
    try:
        await dp.start_polling(bot)
    finally:
        for task in (worker_task, api_task):
            if task is not None:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
