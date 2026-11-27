from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ai_oral_scan.db import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(40), default="field_operator")
    scope_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Municipality(Base):
    __tablename__ = "municipalities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    ibge_code: Mapped[str] = mapped_column(String(7), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    state_uf: Mapped[str] = mapped_column(String(2), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Region(Base):
    __tablename__ = "regions"
    __table_args__ = (UniqueConstraint("municipality_id", "name", name="uq_region_municipality_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    municipality_id: Mapped[str] = mapped_column(ForeignKey("municipalities.id", ondelete="RESTRICT"), index=True)
    name: Mapped[str] = mapped_column(String(160))


class School(Base):
    __tablename__ = "schools"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    municipality_id: Mapped[str] = mapped_column(ForeignKey("municipalities.id", ondelete="RESTRICT"), index=True)
    external_code: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    school_id: Mapped[str] = mapped_column(ForeignKey("schools.id", ondelete="RESTRICT"), index=True)
    name: Mapped[str] = mapped_column(String(180))
    starts_on: Mapped[Date | None] = mapped_column(Date, nullable=True)
    ends_on: Mapped[Date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class StudentIdentity(Base):
    """Restricted identity vault. Never join into analytics or expose from general APIs."""

    __tablename__ = "student_identities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    encrypted_contact_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class StudentSubject(Base):
    """Pseudonymous operational record, separated from direct identity fields."""

    __tablename__ = "student_subjects"
    __table_args__ = (Index("ix_student_subject_school_campaign", "school_id", "campaign_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    pseudonym: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=lambda: str(uuid4()))
    identity_id: Mapped[str | None] = mapped_column(
        ForeignKey("student_identities.id", ondelete="RESTRICT"), unique=True, nullable=True
    )
    school_id: Mapped[str] = mapped_column(ForeignKey("schools.id", ondelete="RESTRICT"), index=True)
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"), index=True)
    age_band: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Screening(Base):
    __tablename__ = "screenings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    subject_id: Mapped[str] = mapped_column(ForeignKey("student_subjects.id", ondelete="RESTRICT"), index=True)
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"), index=True)
    operator_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    idempotency_key: Mapped[str] = mapped_column(String(100), unique=True)
    status: Mapped[str] = mapped_column(String(24), default="draft")
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), index=True)
    resource_type: Mapped[str] = mapped_column(String(80))
    resource_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    scope_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    outcome: Mapped[str] = mapped_column(String(24), default="success")
    correlation_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
