import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.camera import Camera
    from app.models.person import Person


class EventType(str, enum.Enum):
    known = "known"
    unknown = "unknown"


class FaceEvent(Base):
    __tablename__ = "face_events"
    __table_args__ = (
        CheckConstraint(
            "confidence_score >= 0 AND confidence_score <= 1",
            name="confidence_range",
        ),
        CheckConstraint(
            "(event_type = 'known' AND person_name IS NOT NULL) "
            "OR (event_type = 'unknown' AND person_id IS NULL AND person_name IS NULL)",
            name="person_consistency",
        ),
        CheckConstraint(
            "event_type IN ('known', 'unknown')",
            name="event_type",
        ),
        Index("ix_face_events_event_time", "event_time"),
        Index("ix_face_events_person_time", "person_id", "event_time"),
        Index("ix_face_events_camera_time", "camera_id", "event_time"),
        Index("ix_face_events_type_time", "event_type", "event_time"),
        Index("ix_face_events_created_at", "created_at"),
    )

    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    person_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("persons.id", ondelete="SET NULL")
    )
    person_name: Mapped[str | None] = mapped_column(String(100))
    camera_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("cameras.id", ondelete="SET NULL")
    )
    camera_name: Mapped[str] = mapped_column(String(100), nullable=False)
    event_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    event_type: Mapped[str] = mapped_column(String(16), nullable=False)
    snapshot_path: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    person: Mapped["Person | None"] = relationship(back_populates="events")
    camera: Mapped["Camera | None"] = relationship(back_populates="events")
    unknown: Mapped["UnknownEvent | None"] = relationship(
        back_populates="event", uselist=False, cascade="all, delete-orphan"
    )


class UnknownEvent(Base):
    __tablename__ = "unknown_events"
    __table_args__ = (
        CheckConstraint(
            "occurrence_count > 0", name="occurrence_positive"
        ),
        CheckConstraint(
            "last_seen_at >= first_seen_at",
            name="seen_order",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("face_events.event_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    track_id: Mapped[str | None] = mapped_column(String(100))
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    occurrence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    event: Mapped[FaceEvent] = relationship(back_populates="unknown")
