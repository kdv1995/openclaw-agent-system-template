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
3. Give three free video steps:
   - follow-up and lost revenue;
   - bot as segmentation, nurture, FAQ, and handoff system;
   - package, guarantee, support, webinars, and purchase tracking.
4. Close common objections through FAQ.
5. Collect a phone number for a sales consultation call.
6. Run contextual follow-up for people who do not finish the path.

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

## Follow-Up Logic

The bot now has a built-in follow-up worker:

- after diagnosis: reminds the lead to start video 1, then checks back after 3 days;
- after video 1: nudges to video 2 with the segmentation angle;
- after video 2: nudges to video 3 with guarantee/support/tracking angle;
- after FAQ: invites to a consultation if the lead is still evaluating;
- after consultation click: reminds the lead to leave a phone number;
- after phone collection: cancels all pending follow-ups;
- after "Не нагадувати", "стоп", or "stop": opts the lead out.

Follow-up events are stored in Postgres in `followups`, so restarts do not lose scheduled reminders.
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

## Deployment

Deploy the scaffold to any Docker-capable host. Keep hostnames, IP addresses, SSH keys, and platform credentials outside this repository.
