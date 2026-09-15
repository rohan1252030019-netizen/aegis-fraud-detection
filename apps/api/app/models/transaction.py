"""AEGIS - Account and Transaction Database Models"""
from __future__ import annotations
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.enums import RiskLevel, AccountClassification


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (UniqueConstraint("org_id", "account_id", name="uq_account_org_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    account_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    classification: Mapped[str] = mapped_column(String(50), default=AccountClassification.NORMAL)
    risk_level: Mapped[str] = mapped_column(String(50), default=RiskLevel.LOW, index=True)
    individual_risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    network_risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    composite_risk_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    total_transactions: Mapped[int] = mapped_column(Integer, default=0)
    total_sent: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    total_received: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    first_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_watchlisted: Mapped[bool] = mapped_column(Boolean, default=False)
    watchlist_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_false_positive: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (UniqueConstraint("org_id", "transaction_id", name="uq_transaction_org_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_id: Mapped[str] = mapped_column(String(255), nullable=False)
    sender_account_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    receiver_account_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    transaction_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
