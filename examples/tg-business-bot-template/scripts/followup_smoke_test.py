import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

from sqlalchemy import delete, select

PROJECT_ROOT = Path(__file__).resolve().parents[1]

import sys

sys.path.insert(0, str(PROJECT_ROOT))

from bot.config import settings
from bot.db import FollowUp, Lead, SessionLocal, init_db
from bot.main import cancel_pending_followups, run_followup_once, schedule_followups, upsert_lead


TEST_TELEGRAM_ID = 900_000_001


def fake_event() -> SimpleNamespace:
    user = SimpleNamespace(
        id=TEST_TELEGRAM_ID,
        username="smoke_followup",
        full_name="Smoke Followup",
        first_name="Smoke",
    )
    return SimpleNamespace(from_user=user)


async def cleanup() -> None:
    async with SessionLocal() as session:
        lead_result = await session.execute(select(Lead).where(Lead.telegram_id == TEST_TELEGRAM_ID))
        lead = lead_result.scalar_one_or_none()
        if lead is not None:
            await session.execute(delete(FollowUp).where(FollowUp.lead_id == lead.id))
            await session.execute(delete(Lead).where(Lead.id == lead.id))
        await session.commit()


async def main() -> None:
    settings.followup_test_mode = True
    await init_db()
    await cleanup()

    event = fake_event()
    await upsert_lead(
        event,
        business_type="services",
        role="owner",
        monthly_volume="mid",
        scale_problem="followup",
        has_bot="weak",
        current_tools="CRM and manual Telegram reminders",
        urgency="now",
        segment="hot",
        intent="videos_started",
    )
    await schedule_followups(event, ["diagnosis_2h", "nurture_3d"], reset_pending=True)

    async with SessionLocal() as session:
        result = await session.execute(select(FollowUp).where(FollowUp.telegram_id == TEST_TELEGRAM_ID))
        created = list(result.scalars())
        assert len(created) == 2, f"expected 2 followups, got {len(created)}"
        created[0].scheduled_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        await session.commit()

    sent_count = await run_followup_once(bot=None, limit=10)
    assert sent_count == 1, f"expected 1 due followup, got {sent_count}"

    async with SessionLocal() as session:
        sent_result = await session.execute(
            select(FollowUp).where(FollowUp.telegram_id == TEST_TELEGRAM_ID, FollowUp.status == "sent")
        )
        sent = list(sent_result.scalars())
        assert len(sent) == 1, f"expected 1 sent followup, got {len(sent)}"

    cancelled = await cancel_pending_followups(TEST_TELEGRAM_ID, reason="smoke_cancelled")
    assert cancelled == 1, f"expected 1 cancelled pending followup, got {cancelled}"

    await cleanup()
    print("followup smoke test passed")


if __name__ == "__main__":
    asyncio.run(main())
