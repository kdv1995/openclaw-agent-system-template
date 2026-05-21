# OpenClaw Agent System Template: повна документація українською

Це очищений шаблон агентської системи для OpenClaw/Codex. Його можна взяти як базу для персонального AI-операційного простору: головний агент-оркестратор, пам'ять, skills, спеціалісти, runbooks, handoff-процеси, контент-машини, lead-to-landing workflow і приклад Telegram-бота з PostgreSQL.

Шаблон спеціально зібраний без приватних переписок, робочих файлів, ключів, токенів, логів, медіа, клієнтських баз, записів дзвінків і live state. Усі реальні секрети людина має додати локально сама через `.env` або менеджер секретів.

## 1. Що ця система вже вміє

- Працювати як головний персональний агент-оркестратор.
- Зберігати довготривалу пам'ять у workspace-файлах без прив'язки до одного чату.
- Делегувати задачі спеціалістам через чіткі task specs і reports.
- Розділяти короткі задачі, довгі автономні процеси і зовнішні дії.
- Вести lead-to-landing pipeline: ліди, дзвінки, research, UX, visual design, розробка, SEO.
- Підтримувати content/social workflow: research, writing, adaptation, publishing, analytics, learning.
- Давати основу для Telegram-бота з PostgreSQL, сегментацією, follow-up логікою і Docker.
- Працювати зі skills як з переносимими інструкціями: дизайн, безпека, SEO, браузерна перевірка, генерація зображень, транскрибація, publishing.

## 2. Що всередині

```text
agent-workspace/
  AGENTS.template.md      Головні правила агентської системи.
  SOUL.template.md        Тон, стиль, принципи поведінки агента.
  USER.template.md        Шаблон профілю власника системи.
  TOOLS.template.md       Локальні нотатки про інструменти та інтеграції.
  HEARTBEAT.template.md   Нагадування для проактивних перевірок.
  MEMORY.template.md      Порожній шаблон довготривалої пам'яті.

departments/
  inbox/                  Нові задачі для спеціалістів.
  active/                 Прийняті задачі в роботі.
  done/                   Завершені task specs.
  reports/                Звіти спеціалістів.
  runbooks/               Правила комунікації між агентами.

specialists/
  calls-agent/            Дзвінки та ElevenLabs-style voice workflows.
  lead-qualifier/         Підготовка і фільтрація лідів.
  business-researcher/    Публічний research бізнесів.
  ui-ux-designer/         Структура лендингів і конверсійні сценарії.
  visual-designer/        Візуальна система і creative direction.
  full-stack-developer/   Реалізація сайтів/ботів/інтерфейсів.
  seo-optimizer/          SEO, аналітика, tracking.

systems/
  lead-to-landing-os/     Приклад повного агентського pipeline для лендингів.
  social-growth-os/       Приклад контентної/соціальної агентської системи.

skills/
  ...                     Переносимі skills для OpenClaw/Codex.

examples/
  tg-business-bot-template/
                          Telegram-бот з PostgreSQL, Docker і follow-up базою.

docs/
  CAPABILITIES.md         Короткий список можливостей.
  QUICKSTART.md           Швидкий старт.
  SECURITY.md             Модель безпеки.
```

## 3. Як встановити у себе

### Варіант A: як окремий template repository

1. Розархівуй `openclaw-agent-system-template.zip`.
2. Створи новий приватний GitHub repository.
3. Додай файли шаблона в repository.
4. Перевір `.gitignore` і не додавай `.env`, state, logs, memory з реального життя.
5. Відкрий repository через Codex або локальний редактор.

### Варіант B: як workspace для OpenClaw

1. Скопіюй папку `agent-workspace/` у свій OpenClaw workspace.
2. Перейменуй файли:

```text
AGENTS.template.md    -> AGENTS.md
SOUL.template.md      -> SOUL.md
USER.template.md      -> USER.md
TOOLS.template.md     -> TOOLS.md
HEARTBEAT.template.md -> HEARTBEAT.md
MEMORY.template.md    -> MEMORY.md
```

3. Заповни `USER.md`: ім'я, мова, timezone, стиль роботи.
4. Заповни `SOUL.md`: тон агента, принципи, межі.
5. Заповни `TOOLS.md`: тільки локальні підказки, без секретів у Git.
6. Перенеси `departments/`, `skills/`, `systems/`, `specialists/` у workspace.
7. Запусти OpenClaw/Codex у цій папці й попроси агента прочитати `AGENTS.md`.

## 4. Як прогнати через Codex

Після розпакування відкрий папку шаблона в Codex і дай запит:

```text
Прочитай AGENTS.md, README_UA.md і docs/SECURITY.md.
Підготуй цей template під мене:
- запитай тільки те, чого реально бракує;
- створи локальні .env.example файли, але не проси секрети в чаті;
- не додавай приватні переписки, ключі, логи або live state;
- перевір структуру і запропонуй перші 3 автоматизації.
```

Для перевірки перед публікацією можна попросити:

```text
Перевір цей repository на секрети і приватні дані.
Шукай API keys, tokens, Telegram bot tokens, cookies, .env, credentials,
особисті переписки, call transcripts, customer data, live state і generated media.
Не змінюй файли без мого підтвердження, спочатку дай findings.
```

## 5. Головна архітектура

Система тримається на чотирьох шарах:

1. **Main orchestrator**: головний агент, який говорить з людиною, приймає задачі, вирішує чи робити самому, чи делегувати.
2. **Specialists**: агенти за ролями. Вони не пишуть напряму користувачу, а повертають report оркестратору.
3. **Skills**: інструкції та процедурні знання. Вони кажуть агенту, як робити конкретний клас задач.
4. **Durable handoffs**: файли задач і звітів у `departments/`, щоб робота не губилася після перезапуску сесії.

Рекомендований потік:

```text
User request
  -> main orchestrator
  -> task spec у departments/inbox/
  -> specialist accepts у departments/active/
  -> specialist report у departments/reports/
  -> orchestrator verifies
  -> short user-facing result
```

## 6. Як працювати зі спеціалістами

Коли задача чітко належить ролі, оркестратор має створити bounded task:

```text
Owner: ui-ux-designer
Goal: створити структуру лендинга для ...
Inputs: короткий опис бізнесу, аудиторія, офер, приклади
Constraints: без live deploy, без зовнішніх публікацій
Deliverables: wireframe, section copy, CTA flow, blockers
Report format: summary, evidence, files changed, next action
```

Зовнішні дії мають окремі правила:

- outbound calls тільки після явного дозволу на конкретний номер, скрипт і ціль;
- email/social publishing тільки після явного дозволу або durable config;
- live deploy тільки після окремого підтвердження;
- приватні переписки, ключі, customer data і call recordings не виносяться в template.

## 7. Як налаштувати пам'ять

Файли пам'яті:

- `MEMORY.md`: довготривалі факти, рішення, правила, стабільні переваги.
- `memory/YYYY-MM-DD.md`: денні нотатки, raw context, короткі підсумки.
- `TOOLS.md`: локальні технічні нотатки.
- `HEARTBEAT.md`: маленький список регулярних перевірок.

Що можна зберігати:

- стабільні правила роботи;
- важливі рішення;
- назви проєктів;
- не секретні посилання;
- короткі підсумки.

Що не треба зберігати:

- API keys, refresh tokens, cookies;
- приватні переписки повним текстом;
- клієнтські бази;
- записи дзвінків і транскрипти;
- великі JSON dumps;
- production logs.

## 8. Secrets і `.env`

У repository можна тримати тільки `.env.example`.

Правильний патерн:

```text
.env.example            можна комітити
.env                    не можна комітити
credentials.json        не можна комітити
token-state.json        не можна комітити
service-account.json    не можна комітити
```

Приклад `.env.example`:

```bash
TELEGRAM_BOT_TOKEN=replace_me
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/app
OPENAI_API_KEY=replace_me
POSTIZ_API_URL=https://example.com
POSTIZ_API_KEY=replace_me
```

Перед комітом або архівацією запусти перевірку:

```bash
rg -n --hidden --glob '!*.zip' --glob '!.git/**' \
  'sk-[A-Za-z0-9_-]{20,}|xox[baprs]-|ghp_|github_pat_|BEGIN (RSA|OPENSSH|EC|PRIVATE) KEY|bot[0-9]+:|[A-Za-z0-9_-]{24,}\\.[A-Za-z0-9_-]{6,}\\.[A-Za-z0-9_-]{20,}' .
```

Це не замінює повний security review, але ловить багато типових витоків.

## 9. Telegram bot template

`examples/tg-business-bot-template/` дає стартову основу для бота:

- Dockerfile;
- `docker-compose.yml`;
- PostgreSQL;
- `.env.example`;
- базовий bot package;
- follow-up smoke test;
- README для запуску.

Типовий запуск:

```bash
cd examples/tg-business-bot-template
cp .env.example .env
# заповни локальні значення в .env
docker compose up --build
```

Рекомендована логіка бота:

- привітання і пояснення цінності;
- сегментація за типом бізнесу, розміром, болем і готовністю;
- 2-3 корисні відео або матеріали;
- збір заявки;
- follow-up сценарії залежно від сегмента;
- фінальна кнопка на консультацію або дзвінок;
- PostgreSQL як джерело правди для станів, відповідей і follow-up подій.

## 10. Content/social workflow

`systems/social-growth-os/` показує агентську систему для контенту:

- trend scout;
- profile context analyst;
- idea strategist;
- scriptwriter;
- creative director;
- platform adapter;
- publishing ops;
- analytics analyst;
- learning curator.

Публікація назовні має бути тільки після явного дозволу або чітко описаного scheduled config. Для публічного template краще залишати workflow як інструкції, а не live credentials.

## 11. Lead-to-landing workflow

`systems/lead-to-landing-os/` показує повний pipeline:

```text
lead-qualifier
  -> calls-agent
  -> business-researcher
  -> ui-ux-designer
  -> visual-designer
  -> full-stack-developer
  -> seo-optimizer
```

Важливий принцип: якщо бізнес проявив інтерес, спочатку робиться research, а вже потім UX/design/implementation. Це зменшує кількість вигаданих рішень і робить лендинг ближчим до реального бізнесу.

## 12. Як додавати новий skill

Структура:

```text
skills/my-skill/
  SKILL.md
  _meta.json
  references/
  scripts/
  templates/
```

У `SKILL.md` має бути:

- коли skill використовувати;
- які входи потрібні;
- які кроки виконати;
- які команди або scripts запускати;
- як перевірити результат;
- які safety boundaries.

Не клади в skill:

- секрети;
- приватні приклади;
- реальні payloads з клієнтами;
- raw transcripts;
- live cookies або tokens.

## 13. Як підготувати систему до публікації

Перед тим як відправляти template в Telegram-канал або GitHub:

1. Видали `.env`, `.env.*`, credentials, token states.
2. Видали `memory/`, якщо там є особистий контекст.
3. Видали `state/`, `logs/`, `runs/`, `media/`, `recordings/`, `transcripts/`.
4. Перевір `.gitignore`.
5. Запусти secret scan.
6. Відкрий архів і перевір список файлів.
7. Переконайся, що README пояснює setup без приватних даних.

Команда для перегляду архіву:

```bash
unzip -l openclaw-agent-system-template.zip | less
```

Команда для швидкого пошуку небезпечних назв:

```bash
unzip -l openclaw-agent-system-template.zip | rg -i 'env|secret|token|credential|cookie|session|transcript|recording|private|memory|state|log'
```

Якщо знаходиш збіг, це не завжди витік, але треба вручну перевірити файл.

## 14. Рекомендований перший день після встановлення

1. Заповнити `USER.md`, `SOUL.md`, `TOOLS.md`.
2. Створити приватний `.env` локально, не в Git.
3. Попросити Codex перевірити структуру.
4. Обрати один workflow: Telegram bot, lead-to-landing або social-growth.
5. Запустити маленький smoke test без зовнішніх дій.
6. Додати перший власний runbook.
7. Зробити перший приватний commit.

## 15. Що людина має змінити під себе

- Ім'я, мову, timezone і стиль агента.
- Список спеціалістів і їхні ролі.
- Дозволені та заборонені зовнішні дії.
- Канали комунікації: Telegram, Slack, email, calendar.
- Secrets provider: `.env`, 1Password, Doppler, Vault або інше.
- Системи для публікації, CRM, аналітики.
- Власні skills і runbooks.

## 16. Важливі межі

Цей template не є готовою production-системою з гарантіями безпеки. Це стартова архітектура. Перед production використанням треба:

- налаштувати секрети;
- обмежити права токенів;
- зробити audit логування;
- перевірити permissions для зовнішніх інтеграцій;
- додати backup strategy;
- додати human approval для ризикових дій;
- протестувати всі workflow на sandbox даних.

## 17. Короткий опис для Telegram-каналу

Можна використати такий опис:

```text
Це очищений template моєї OpenClaw/Codex агентської системи.

Всередині:
- головний агент-оркестратор;
- workspace memory шаблони;
- skills;
- specialist agents;
- lead-to-landing workflow;
- social/content workflow;
- Telegram bot template з PostgreSQL і Docker;
- українська документація;
- security checklist.

У шаблоні немає ключів, приватних переписок, токенів, клієнтських файлів, логів або live state.
Людина може взяти архів, прогнати через Codex, заповнити свої дані і зібрати власну агентську систему.
```

## 18. Мінімальний security checklist

Перед публікацією має бути true:

- [ ] Немає `.env` файлів.
- [ ] Немає реальних токенів.
- [ ] Немає Telegram bot token.
- [ ] Немає GitHub/Google/Meta/Postiz/ElevenLabs credentials.
- [ ] Немає приватних переписок.
- [ ] Немає `MEMORY.md` з особистим контекстом, тільки `MEMORY.template.md`.
- [ ] Немає call transcripts або recordings.
- [ ] Немає customer/lead datasets.
- [ ] Немає generated media з реальних кампаній.
- [ ] Архів перевірено через `unzip -l` і `rg`.

## 19. Що робити, якщо Codex знайшов секрет

1. Не публікуй архів.
2. Видали файл із template.
3. Якщо секрет уже був у Git history, перепакуй repository без history або перепиши history.
4. Rotate/revoke скомпрометований ключ у провайдера.
5. Перезапусти secret scan.
6. Тільки після clean scan роби новий zip.

## 20. Головний принцип

Публічний template має передавати архітектуру, процеси, ролі, runbooks і приклади. Він не має передавати життя власника системи: приватні діалоги, токени, клієнтів, історію задач, логи і production state.
