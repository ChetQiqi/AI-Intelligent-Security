from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models import EventType
from app.schemas import (
    CameraCreate,
    CameraRead,
    EventCreate,
    EventPage,
    EventRead,
    PersonCreate,
    PersonRead,
)
from app.api.v1.agent import router as agent_router
from app.api.v1.nl2sql import router as nl2sql_router
from app.api.v1.rag import router as rag_router
from app.api.v1.stats import router as stats_router
from app.services.camera_service import create_camera
from app.services.event_service import create_event, list_events
from app.services.person_service import create_person


router = APIRouter(prefix="/api/v1")
router.include_router(agent_router)
router.include_router(nl2sql_router)
router.include_router(rag_router)
router.include_router(stats_router)


@router.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="数据库不可用") from exc
    return {"status": "ok", "database": "ok"}


@router.post("/persons", response_model=PersonRead, status_code=201)
def add_person(payload: PersonCreate, db: Session = Depends(get_db)):
    return create_person(db, payload)


@router.post("/cameras", response_model=CameraRead, status_code=201)
def add_camera(payload: CameraCreate, db: Session = Depends(get_db)):
    return create_camera(db, payload)


@router.post("/events", response_model=EventRead, status_code=201)
def add_event(payload: EventCreate, db: Session = Depends(get_db)):
    return create_event(db, payload)


def _pagination(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    return limit, offset


@router.get("/events/recent", response_model=EventPage)
def recent_events(
    pagination: tuple[int, int] = Depends(_pagination),
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    db: Session = Depends(get_db),
):
    return list_events(
        db,
        limit=pagination[0],
        offset=pagination[1],
        start_time=start_time,
        end_time=end_time,
    )


@router.get("/events/persons/{person_id}", response_model=EventPage)
def events_by_person(
    person_id: int,
    pagination: tuple[int, int] = Depends(_pagination),
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    db: Session = Depends(get_db),
):
    return list_events(
        db,
        limit=pagination[0],
        offset=pagination[1],
        start_time=start_time,
        end_time=end_time,
        person_id=person_id,
        event_type=EventType.known,
    )


@router.get("/events/cameras/{camera_id}", response_model=EventPage)
def events_by_camera(
    camera_id: int,
    pagination: tuple[int, int] = Depends(_pagination),
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    db: Session = Depends(get_db),
):
    return list_events(
        db,
        limit=pagination[0],
        offset=pagination[1],
        start_time=start_time,
        end_time=end_time,
        camera_id=camera_id,
    )


@router.get("/events/unknown", response_model=EventPage)
def unknown_events(
    pagination: tuple[int, int] = Depends(_pagination),
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    db: Session = Depends(get_db),
):
    return list_events(
        db,
        limit=pagination[0],
        offset=pagination[1],
        start_time=start_time,
        end_time=end_time,
        event_type=EventType.unknown,
    )
