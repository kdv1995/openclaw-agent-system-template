# Telegram Business Scaling Bot

Bot flow for businesses that hit a scaling ceiling and need automation, funnels, support, webinars, and consulting.

## Run Locally

1. Copy `.env.example` to `.env`.
2. Add `BOT_TOKEN`.
3. Run:

```bash
docker compose up --build
```

## Core Flow

1. Segment the lead by business type, role, monthly volume, scaling bottleneck, current bot/CRM state, current tools, and urgency.
2. Save every lead and answer in Postgres.
3. Save a long-form strategic-session brief through `/brief`.
4. Use the brief as context for avatar, business pains, funnel gaps, and first automation-process analysis.
5. Show one short sales video that frames the core problem: warm leads do not reach the next business step.
6. Invite the lead to a consultation immediately after the video and again through a 3-minute follow-up.
7. Run contextual follow-up only for people who do not book or leave a phone number.

## Lead Fields

- Telegram ID, username, full name
- phone
- business type
- role
- monthly volume
- scale problem
- existing bot/CRM state
- current tools
- urgency
- segment: `hot` or `nurture`
- intent and notes
- follow-up opt-out flag and last follow-up stage

## Strategic Session Brief

The bot exposes `/brief` and the `📋 Бриф` menu button.

The brief flow is a short Ukrainian business pre-brief with 8 steps:

- business niche, product/service, market;
- main client and client need;
- current business goal;
- biggest sales/request bottleneck;
- current lead path after first contact;
- current tools: site, Instagram, Telegram, CRM, bot, ads, managers;
- product/offer and average check;
- urgency and expected timeline.

Completed briefs are saved in Postgres table `brief_submissions` as raw JSON plus a formatted Telegram-ready text copy.

## CRM Conversation API

The bot records inbound Telegram messages and button clicks in Postgres table `conversation_messages`.
CRM tools can read leads, read a client's conversation history, and send manager replies through the Telegram bot.

Local API:

- `GET /health`
- `GET /crm/leads?limit=50&offset=0`
- `GET /crm/leads/{telegram_id}/messages?limit=100`
- `POST /crm/leads/{telegram_id}/messages` with JSON body `{"text":"...", "sent_by":"manager name"}`

The API is bound to `127.0.0.1:8000` by Docker Compose. Set `CRM_API_KEY` to require the `X-CRM-API-Key` header.

## SendPulse CRM Sync

The bot can sync a consultation lead to SendPulse CRM after a phone number is collected.

Set these environment variables:

- `SENDPULSE_CRM_ENABLED=true`
- `SENDPULSE_API_KEY` — static SendPulse API key used as `Authorization: Bearer <key>`
- `SENDPULSE_RESPONSIBLE_ID` — SendPulse team member ID
- `SENDPULSE_PIPELINE_ID` — target CRM pipeline ID
- `SENDPULSE_STEP_ID` — target pipeline step ID
- `SENDPULSE_DEAL_PRICE` — optional default deal amount
- `SENDPULSE_DEAL_CURRENCY` — `UAH`, `USD`, or `EUR`

When enabled, the bot searches a contact by phone, creates one if needed, creates a deal, and writes the brief/lead context as contact and deal notes. Local sync status is stored on the lead as `sendpulse_sync_status`, `sendpulse_contact_id`, and `sendpulse_deal_id`.

## Admin Sales Dashboard

Set `ADMIN_TELEGRAM_IDS` to a comma-separated list of Telegram user IDs that can see internal sales data.

Admins get an extra `📈 Sales dashboard` keyboard button and can type `/sales`. The public Telegram command menu does not expose this command. Non-admin users who type it receive an access-denied message.

The dashboard shows:

- total leads, hot/nurture split, phone captures, consultation requests, and opt-outs;
- pending/sent/failed follow-ups;
- latest updated leads with segment, intent, phone state, business type, and problem;
- the current `leads` database fields.

## Follow-Up Logic

The bot has a built-in follow-up worker:

- after brief start: reminds the lead to finish the brief;
- after brief completion or sales-video view: invites the lead to consultation after 3 minutes;
- after brief completion: sends a longer fallback reminder after 20 hours;
- after consultation click: reminds the lead to leave a phone number;
- after phone collection: cancels all pending follow-ups;
- after "Не нагадувати", "стоп", or "stop": opts the lead out.

Follow-up events are stored in Postgres in `followups`, so restarts do not lose scheduled reminders.

## Telegram Commands

The production bot exposes a Telegram command menu:

- `/start` — open the brief and then the sales-video/consultation path
- `/brief` — fill in the strategic-session brief
- `/videos` — show the short sales video
- `/consultation` — ask for a phone number and create a consultation intent
- `/stop` — opt out of pending follow-up reminders
- `/help` — explain what the bot can do
Use `FOLLOWUP_ENABLED=false` to disable sending and `FOLLOWUP_POLL_SECONDS` to tune the worker interval.

## Test

With Postgres running:

```bash
docker compose up -d postgres
DATABASE_URL=postgresql+asyncpg://bot:bot_password@localhost:5432/business_bot \
BOT_TOKEN=smoke:test \
FOLLOWUP_TEST_MODE=true \
python scripts/followup_smoke_test.py
```

## Deployment Host

GCP VM:

- Project: `project-05c1ef1c-2283-427c-9dc`
- Zone: `europe-central2-a`
- Instance: `tg-bot-ua-1`
- External IP: `34.158.230.169`
- SSH: `ssh -i ~/.ssh/tg_bot_ua_1 user@34.158.230.169`

The same scaffold is deployed on the VM at `/opt/tg-business-bot`.
