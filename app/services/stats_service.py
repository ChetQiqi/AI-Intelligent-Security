from datetime import datetime, timedelta, timezone

from sqlalchemy import case, desc, func, select
from sqlalchemy.orm import Session

from app.models import Camera, EventType, FaceEvent, Person
from app.schemas.stats import (
    CameraActivityItem,
    CameraActivityResponse,
    CameraRankingItem,
    CameraRankingResponse,
    PersonRankingItem,
    PersonRankingResponse,
    StatsSummary,
    UnknownTrendItem,
    UnknownTrendResponse,
)


def get_stats_summary(db: Session) -> StatsSummary:
    today_start = datetime.combine(
        datetime.now(timezone.utc).date(),
        datetime.min.time(),
        tzinfo=timezone.utc,
    )
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    total_events = db.scalar(select(func.count()).select_from(FaceEvent)) or 0
    unknown_events = (
        db.scalar(
            select(func.count())
            .select_from(FaceEvent)
            .where(FaceEvent.event_type == EventType.unknown.value)
        )
        or 0
    )
    recent_events = (
        db.scalar(
            select(func.count())
            .select_from(FaceEvent)
            .where(FaceEvent.event_time >= seven_days_ago)
        )
        or 0
    )
    today_known_persons = (
        db.scalar(
            select(func.count(func.distinct(FaceEvent.person_id)))
            .select_from(FaceEvent)
            .where(FaceEvent.event_type == EventType.known.value)
            .where(FaceEvent.event_time >= today_start)
            .where(FaceEvent.person_id.is_not(None))
        )
        or 0
    )
    return StatsSummary(
        total_events=total_events,
        unknown_events=unknown_events,
        recent_events=recent_events,
        today_known_persons=today_known_persons,
    )


def get_camera_ranking(db: Session, *, limit: int) -> CameraRankingResponse:
    event_count = func.count().label("event_count")
    statement = (
        select(FaceEvent.camera_id, FaceEvent.camera_name, event_count)
        .group_by(FaceEvent.camera_id, FaceEvent.camera_name)
        .order_by(desc(event_count), FaceEvent.camera_name.asc())
        .limit(limit)
    )
    return CameraRankingResponse(
        items=[
            CameraRankingItem(
                camera_id=row.camera_id,
                camera_name=row.camera_name,
                event_count=row.event_count,
            )
            for row in db.execute(statement)
        ]
    )


def get_camera_activity(db: Session, *, days: int) -> CameraActivityResponse:
    start_at = datetime.now(timezone.utc) - timedelta(days=days)
    event_count = func.count(FaceEvent.event_id).label("event_count")
    unknown_count = func.sum(
        case((FaceEvent.event_type == EventType.unknown.value, 1), else_=0)
    ).label("unknown_count")
    last_event_time = func.max(FaceEvent.event_time).label("last_event_time")
    statement = (
        select(
            Camera.id,
            Camera.name,
            Camera.status,
            event_count,
            unknown_count,
            last_event_time,
        )
        .outerjoin(
            FaceEvent,
            (FaceEvent.camera_id == Camera.id) & (FaceEvent.event_time >= start_at),
        )
        .group_by(Camera.id, Camera.name, Camera.status)
        .order_by(desc(event_count), Camera.name.asc())
    )
    return CameraActivityResponse(
        items=[
            CameraActivityItem(
                camera_id=row.id,
                camera_name=row.name,
                status=row.status,
                event_count=row.event_count or 0,
                unknown_count=row.unknown_count or 0,
                last_event_time=_format_datetime(row.last_event_time),
            )
            for row in db.execute(statement)
        ]
    )


def get_person_ranking(db: Session, *, limit: int) -> PersonRankingResponse:
    event_count = func.count(FaceEvent.event_id).label("event_count")
    statement = (
        select(
            FaceEvent.person_id,
            FaceEvent.person_name,
            Person.department,
            event_count,
        )
        .join(Person, Person.id == FaceEvent.person_id)
        .where(FaceEvent.event_type == EventType.known.value)
        .where(FaceEvent.person_id.is_not(None))
        .group_by(FaceEvent.person_id, FaceEvent.person_name, Person.department)
        .order_by(desc(event_count), FaceEvent.person_name.asc())
        .limit(limit)
    )
    return PersonRankingResponse(
        items=[
            PersonRankingItem(
                person_id=row.person_id,
                person_name=row.person_name,
                department=row.department,
                event_count=row.event_count,
            )
            for row in db.execute(statement)
        ]
    )


def get_unknown_trend(db: Session, *, days: int) -> UnknownTrendResponse:
    today = datetime.now(timezone.utc).date()
    start_date = today - timedelta(days=days - 1)
    start_at = datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc)
    statement = (
        select(FaceEvent.event_time)
        .where(FaceEvent.event_type == EventType.unknown.value)
        .where(FaceEvent.event_time >= start_at)
    )
    counts = {str(start_date + timedelta(days=index)): 0 for index in range(days)}
    for event_time in db.scalars(statement):
        event_date = event_time.date().isoformat()
        if event_date in counts:
            counts[event_date] += 1
    return UnknownTrendResponse(
        items=[
            UnknownTrendItem(date=event_date, unknown_count=count)
            for event_date, count in counts.items()
        ]
    )


def _format_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
