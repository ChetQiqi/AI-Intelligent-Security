from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.event import EventType


class UnknownEventCreate(BaseModel):
    track_id: str | None = Field(default=None, max_length=100)
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None
    occurrence_count: int = Field(default=1, gt=0)
    notes: str | None = None

    @model_validator(mode="after")
    def validate_seen_order(self):
        if (
            self.first_seen_at is not None
            and self.last_seen_at is not None
            and self.last_seen_at < self.first_seen_at
        ):
            raise ValueError("last_seen_at 不能早于 first_seen_at")
        return self


class EventCreate(BaseModel):
    event_type: EventType
    person_id: int | None = Field(default=None, gt=0)
    camera_id: int = Field(gt=0)
    event_time: datetime | None = None
    confidence_score: Decimal = Field(ge=0, le=1)
    snapshot_path: str | None = Field(default=None, max_length=500)
    unknown: UnknownEventCreate | None = None

    @model_validator(mode="after")
    def validate_event_shape(self):
        if self.event_type == EventType.known:
            if self.person_id is None:
                raise ValueError("known 事件必须提供 person_id")
            if self.unknown is not None:
                raise ValueError("known 事件不能包含 unknown 扩展")
        elif self.person_id is not None:
            raise ValueError("unknown 事件不能提供 person_id")
        return self


class UnknownEventRead(BaseModel):
    id: int
    track_id: str | None
    first_seen_at: datetime
    last_seen_at: datetime
    occurrence_count: int
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventRead(BaseModel):
    event_id: UUID
    person_id: int | None
    person_name: str | None
    camera_id: int | None
    camera_name: str
    event_time: datetime
    confidence_score: Decimal
    event_type: EventType
    snapshot_path: str | None
    created_at: datetime
    unknown: UnknownEventRead | None

    model_config = ConfigDict(from_attributes=True)


class EventPage(BaseModel):
    items: list[EventRead]
    total: int
    limit: int
    offset: int
