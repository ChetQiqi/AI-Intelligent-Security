from pydantic import BaseModel


class StatsSummary(BaseModel):
    total_events: int
    unknown_events: int
    recent_events: int
    today_known_persons: int


class CameraRankingItem(BaseModel):
    camera_id: int | None
    camera_name: str
    event_count: int


class CameraRankingResponse(BaseModel):
    items: list[CameraRankingItem]


class CameraActivityItem(BaseModel):
    camera_id: int
    camera_name: str
    status: str
    event_count: int
    unknown_count: int
    last_event_time: str | None


class CameraActivityResponse(BaseModel):
    items: list[CameraActivityItem]


class PersonRankingItem(BaseModel):
    person_id: int
    person_name: str
    department: str | None
    event_count: int


class PersonRankingResponse(BaseModel):
    items: list[PersonRankingItem]


class UnknownTrendItem(BaseModel):
    date: str
    unknown_count: int


class UnknownTrendResponse(BaseModel):
    items: list[UnknownTrendItem]
