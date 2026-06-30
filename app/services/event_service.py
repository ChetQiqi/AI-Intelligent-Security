from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Camera, EventType, FaceEvent, Person, UnknownEvent
from app.schemas.event import EventCreate, EventPage
from app.services.exceptions import NotFoundError


def create_event(db: Session, payload: EventCreate) -> FaceEvent:
    camera = db.get(Camera, payload.camera_id)
    if camera is None:
        raise NotFoundError(f"摄像头不存在: {payload.camera_id}")

    person = None
    if payload.event_type == EventType.known:
        person = db.get(Person, payload.person_id)
        if person is None:
            raise NotFoundError(f"人员不存在: {payload.person_id}")

    event_time = payload.event_time or datetime.now(timezone.utc)
    event = FaceEvent(
        person_id=person.id if person else None,
        person_name=person.name if person else None,
        camera_id=camera.id,
        camera_name=camera.name,
        event_time=event_time,
        confidence_score=payload.confidence_score,
        event_type=payload.event_type.value,
        snapshot_path=payload.snapshot_path,
    )
    if payload.event_type == EventType.unknown:
        detail = payload.unknown
        first_seen = detail.first_seen_at if detail and detail.first_seen_at else event_time
        last_seen = detail.last_seen_at if detail and detail.last_seen_at else first_seen
        event.unknown = UnknownEvent(
            track_id=detail.track_id if detail else None,
            first_seen_at=first_seen,
            last_seen_at=last_seen,
            occurrence_count=detail.occurrence_count if detail else 1,
            notes=detail.notes if detail else None,
        )

    db.add(event)
    db.commit()
    query = (
        select(FaceEvent)
        .options(selectinload(FaceEvent.unknown))
        .where(FaceEvent.event_id == event.event_id)
    )
    return db.scalar(query)


def list_events(
    db: Session,
    *,
    limit: int,
    offset: int,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    person_id: int | None = None,
    camera_id: int | None = None,
    event_type: EventType | None = None,
) -> EventPage:
    filters = []
    if start_time is not None:
        filters.append(FaceEvent.event_time >= start_time)
    if end_time is not None:
        filters.append(FaceEvent.event_time <= end_time)
    if person_id is not None:
        filters.append(FaceEvent.person_id == person_id)
    if camera_id is not None:
        filters.append(FaceEvent.camera_id == camera_id)
    if event_type is not None:
        filters.append(FaceEvent.event_type == event_type.value)

    total = db.scalar(select(func.count()).select_from(FaceEvent).where(*filters)) or 0
    statement = (
        select(FaceEvent)
        .options(selectinload(FaceEvent.unknown))
        .where(*filters)
        .order_by(FaceEvent.event_time.desc(), FaceEvent.event_id.desc())
        .limit(limit)
        .offset(offset)
    )
    return EventPage(
        items=list(db.scalars(statement).all()),
        total=total,
        limit=limit,
        offset=offset,
    )
