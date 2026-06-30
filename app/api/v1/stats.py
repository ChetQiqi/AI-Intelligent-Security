from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.stats import (
    CameraActivityResponse,
    CameraRankingResponse,
    PersonRankingResponse,
    StatsSummary,
    UnknownTrendResponse,
)
from app.services.stats_service import (
    get_camera_activity,
    get_camera_ranking,
    get_person_ranking,
    get_stats_summary,
    get_unknown_trend,
)


router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/summary", response_model=StatsSummary)
def stats_summary(db: Session = Depends(get_db)):
    return get_stats_summary(db)


@router.get("/cameras/ranking", response_model=CameraRankingResponse)
def camera_ranking(
    limit: int = Query(default=5, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return get_camera_ranking(db, limit=limit)


@router.get("/cameras/activity", response_model=CameraActivityResponse)
def camera_activity(
    days: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db),
):
    return get_camera_activity(db, days=days)


@router.get("/persons/ranking", response_model=PersonRankingResponse)
def person_ranking(
    limit: int = Query(default=5, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return get_person_ranking(db, limit=limit)


@router.get("/unknown/trend", response_model=UnknownTrendResponse)
def unknown_trend(
    days: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db),
):
    return get_unknown_trend(db, days=days)
