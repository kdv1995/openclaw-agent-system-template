from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, func, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .config import settings


class Base(DeclarativeBase):
    pass


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    business_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    monthly_volume: Mapped[str | None] = mapped_column(String(255), nullable=True)
    scale_problem: Mapped[str | None] = mapped_column(String(255), nullable=True)
    has_bot: Mapped[str | None] = mapped_column(String(32), nullable=True)
    current_tools: Mapped[str | None] = mapped_column(Text, nullable=True)
    urgency: Mapped[str | None] = mapped_column(String(64), nullable=True)
    segment: Mapped[str | None] = mapped_column(String(64), nullable=True)
    intent: Mapped[str | None] = mapped_column(String(64), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    followup_opt_out: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    last_followup_stage: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sendpulse_contact_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sendpulse_deal_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sendpulse_sync_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    sendpulse_sync_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    sendpulse_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FollowUp(Base):
    __tablename__ = "followups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True)
    stage: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", server_default="pending", index=True)
    message_text: Mapped[str] = mapped_column(Text)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BriefSubmission(Base):
    __tablename__ = "brief_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    data_json: Mapped[str] = mapped_column(Text)
    formatted_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    direction: Mapped[str] = mapped_column(String(16), index=True)
    message_type: Mapped[str] = mapped_column(String(32), default="text", server_default="text")
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="telegram", server_default="telegram", index=True)
    sent_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telegram_message_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    reply_to_message_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


engine = create_async_engine(settings.database_url)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS full_name VARCHAR(255)"))
        await conn.execute(text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS phone VARCHAR(64)"))
        await conn.execute(text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS role VARCHAR(255)"))
        await conn.execute(text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS monthly_volume VARCHAR(255)"))
        await conn.execute(text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS current_tools TEXT"))
        await conn.execute(text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS urgency VARCHAR(64)"))
        await conn.execute(text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS followup_opt_out INTEGER DEFAULT 0"))
        await conn.execute(text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS last_followup_stage VARCHAR(64)"))
        await conn.execute(text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS sendpulse_contact_id INTEGER"))
        await conn.execute(text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS sendpulse_deal_id INTEGER"))
        await conn.execute(text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS sendpulse_sync_status VARCHAR(32)"))
        await conn.execute(text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS sendpulse_sync_error TEXT"))
        await conn.execute(text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS sendpulse_synced_at TIMESTAMP WITH TIME ZONE"))
