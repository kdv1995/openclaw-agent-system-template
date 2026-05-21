# Prompt Playbook для агентської системи

Ця папка містить готові шаблони промптів для роботи з головним оркестратором і спеціалістами. Їх можна вставляти в Codex/OpenClaw і адаптувати під свою задачу.

Головна ідея: не просити агента "зробити щось", а дати йому роль, контекст, межі, вхідні дані, очікувані deliverables і формат звіту.

## 1. Базова структура задачі для оркестратора

```text
Ти головний оркестратор моєї агентської системи.

Задача:
<що треба зробити>

Контекст:
- Проєкт: <назва або папка>
- Бізнес/ніша: <коротко>
- Цільова аудиторія: <хто має отримати результат>
- Поточний стан: <що вже є>
- Обмеження: <чого не можна робити>

Роль оркестратора:
1. Розбери задачу.
2. Визнач, що зробити самому, а що делегувати спеціалістам.
3. Для кожного спеціаліста створи bounded task: owner, goal, inputs, constraints, allowed external actions, deliverables, report format.
4. Не роби зовнішніх дій без мого окремого дозволу.
5. Після виконання перевір результат і дай короткий підсумок.

Критерій готовності:
<як зрозуміти, що задача завершена>
```

## 2. Шаблон делегування спеціалісту

```text
Owner: <agent-name>
Requested by: main orchestrator
Priority: normal|high|urgent
External action allowed: no|yes, scope: <чіткий дозвіл>

Goal:
<одне речення про результат>

Inputs:
- Files/paths:
- Business context:
- User request:
- Existing constraints:

Rules:
- Не розширюй scope без дозволу.
- Не публікуй, не дзвони, не деплой без explicit permission.
- Не використовуй приватні переписки, секрети або live state, якщо вони не потрібні для задачі.
- Якщо бракує даних, поверни blocker замість здогадок.

Deliverables:
- <файл/звіт/код/специфікація>
- <перевірка або evidence>

Report format:
Status: completed|partial|blocked
Changed:
Evidence:
Blockers:
Next suggested action:
```

## 3. Як просити оркестратора розкласти задачу по агентам

```text
Розклади цю задачу по спеціалістах і виконай через агентську систему.

Задача:
<опис>

Доступні ролі:
- lead-qualifier: підготовка і фільтрація лідів;
- calls-agent: approved outbound calls, transcripts, recordings, statuses;
- business-researcher: public research і контекст бізнесу;
- ui-ux-designer: структура лендинга, conversion flow, copy blocks;
- visual-designer: visual direction, creative assets, style system;
- full-stack-developer: implementation, local verification, code;
- seo-optimizer: metadata, tracking, local SEO, technical SEO;
- publishing-ops: scheduling, Postiz/social publishing, publishing reports;
- memory-curator: memory capture, archive, summarization.

Твоя робота:
1. Визнач, які ролі потрібні.
2. Не делегуй зайве.
3. Для кожної ролі напиши task spec.
4. Виконай або підготуй handoff.
5. Після reports зроби verification і дай мені результат.

Заборонено:
- робити зовнішні дії без мого дозволу;
- додавати ключі, токени, приватні переписки або клієнтські бази в файли;
- деплоїти без explicit approval.
```

## 4. Lead-to-landing prompt

```text
Запусти lead-to-landing workflow як оркестратор.

Ціль:
З ліда або списку лідів дійти до готової структури лендинга / прототипу / локальної реалізації.

Вхідні дані:
- Джерело лідів: <sheet/file/source>
- Scope: <точні rows/range або конкретні контакти>
- Caller ID: <номер, якщо потрібні дзвінки>
- Offer/script: <що пропонуємо>
- Stop conditions: <коли зупинитись>

Порядок:
1. lead-qualifier: перевірити валідність і пріоритети.
2. calls-agent: тільки якщо явно дозволені дзвінки.
3. business-researcher: для зацікавлених бізнесів.
4. ui-ux-designer: структура лендинга і CTA flow.
5. visual-designer: visual direction і assets.
6. full-stack-developer: локальна реалізація.
7. seo-optimizer: SEO/tracking review.

Rules:
- Дзвінки тільки one by one і тільки в approved scope.
- Якщо бізнес зацікавлений, спочатку research, потім UX/design/dev.
- Live deploy заборонений без окремого дозволу.
- У фінальному звіті дай evidence: files, paths, tests, blockers.
```

## 5. Prompt для Telegram-бота з сегментацією і follow-up

```text
Спроєктуй і реалізуй Telegram-бота для бізнес-аудиторії.

Мета бота:
Провести людину через 2-3 корисні матеріали, зібрати сегментацію, зрозуміти біль бізнесу, прогріти follow-up повідомленнями і довести до консультації.

Контекст:
- Трафік приходить з лендинга.
- Аудиторія: бізнеси, які мають проблему масштабування, продажів, follow-up або операційки.
- База: PostgreSQL.
- Запуск: Docker/Docker Compose.

Функціонал:
1. Welcome flow з професійним тоном.
2. Сегментаційні питання: тип бізнесу, розмір, головний біль, готовність до рішення.
3. Збереження відповідей у PostgreSQL.
4. Видача 2-3 матеріалів/відео.
5. Follow-up сценарії за сегментами.
6. Кнопка консультації з переходом на дзвінок/контакт.
7. Admin/reporting view або export, якщо доречно.

Deliverables:
- Архітектура.
- DB schema.
- Bot flow.
- Follow-up schedule.
- Код.
- Docker setup.
- Smoke tests.

Security:
- Не коміть реальний bot token.
- Використовуй `.env.example`.
- Перед фіналом перевір repo на токени і секрети.
```

## 6. Prompt для content/social workflow

```text
Запусти content workflow для <платформа/ніша>.

Ціль:
Створити і підготувати контент-пакет, який можна опублікувати через approved publishing flow.

Ролі:
- research-agent: знайти сигнал/інсайт;
- writer-agent: написати пост;
- platform-adapter: адаптувати під платформу;
- visual-designer або image flow: створити тематичний visual;
- publishing-ops: запланувати/опублікувати тільки якщо є дозвіл;
- analytics/learning: зафіксувати результат.

Inputs:
- Тема:
- Аудиторія:
- Тон:
- Платформа:
- Обмеження:
- Чи дозволено publishing: yes/no, scope:

Rules:
- Фактичні твердження перевіряти по credible sources.
- Не публікувати без explicit approval або durable config.
- Для кожної публікації потрібен окремий visual, якщо це вимагає платформа.

Deliverables:
- Final post text.
- Visual status/path.
- Scheduling/publishing status.
- Evidence IDs/links.
- Blockers.
```

## 7. Prompt для security review перед публікацією template

```text
Перевір цей repository на секрети і приватні дані.

Шукай:
- API keys, bot tokens, OAuth tokens, cookies;
- `.env`, credentials, service accounts;
- private memory, personal chats, customer data;
- call transcripts, recordings, logs;
- generated media, archives, live state;
- GitHub/Telegram/Google/Meta/Postiz/ElevenLabs secrets.

Rules:
- Не змінюй файли без мого підтвердження, спочатку дай findings.
- Відрізняй реальні секрети від placeholder-ів типу `replace_me`.
- Для кожної знахідки дай file path, line, risk, recommended action.

Після мого дозволу:
1. Прибери або заміни секрети.
2. Онови `.gitignore`.
3. Перевір архів.
4. Дай фінальний security summary.
```

## 8. Prompt для локальної перевірки після змін

```text
Перевір зміни перед фіналом.

Зроби:
1. `git status --short`
2. Перевір relevant files вручну.
3. Запусти tests/lint/build, якщо вони є.
4. Перевір security patterns, якщо задача торкається template/public repo.
5. Якщо є архів, перевір його вміст через `zipinfo`.

Фінальний звіт:
- Що змінено.
- Які команди/перевірки пройшли.
- Що не перевірено і чому.
- Чи потрібна дія від людини.
```

## 9. Формула якісного prompt

Кожна складна задача має відповідати на сім питань:

1. **Role**: хто має виконувати задачу?
2. **Goal**: який результат потрібен?
3. **Context**: що вже відомо?
4. **Inputs**: які файли, дані, посилання або constraints використовувати?
5. **Boundaries**: чого не можна робити?
6. **Deliverables**: що саме здати?
7. **Evidence**: як довести, що задача зроблена?

Якщо хоча б одного пункту немає, оркестратор має або зробити обережне припущення, або поставити коротке уточнення.
