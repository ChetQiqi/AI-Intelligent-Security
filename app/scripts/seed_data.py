import argparse
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import delete, insert

from app.db.session import SessionLocal
from app.models import Camera, FaceEvent, Person, UnknownEvent


DEPARTMENTS = ["研发部", "行政部", "安保部", "财务部", "运营部"]
CAMERA_PRESETS = [
    ("CAM-NORTH", "北门摄像头", "园区北门"),
    ("CAM-SOUTH", "南门摄像头", "园区南门"),
    ("CAM-LOBBY", "大厅摄像头", "办公楼一层大厅"),
    ("CAM-PARKING", "停车场摄像头", "地下停车场入口"),
    ("CAM-OFFICE", "办公区摄像头", "办公楼三层"),
]


def build_person_rows(count: int) -> list[dict]:
    return [
        {
            "external_id": f"EMP-{index:04d}",
            "name": f"模拟人员{index:02d}",
            "gender": "male" if index % 2 else "female",
            "department": DEPARTMENTS[(index - 1) % len(DEPARTMENTS)],
            "status": "active",
        }
        for index in range(1, count + 1)
    ]


def build_camera_rows(count: int) -> list[dict]:
    rows = []
    for index in range(count):
        if index < len(CAMERA_PRESETS):
            code, name, location = CAMERA_PRESETS[index]
        else:
            code = f"CAM-{index + 1:03d}"
            name = f"扩展摄像头{index + 1:02d}"
            location = f"扩展区域{index + 1:02d}"
        rows.append(
            {
                "code": code,
                "name": name,
                "location": location,
                "status": "online",
            }
        )
    return rows


def _weighted_event_time(
    rng: random.Random, now: datetime, days: int
) -> datetime:
    for _ in range(20):
        candidate_day = now.date() - timedelta(days=rng.randrange(days))
        hour_weights = [
            1,
            1,
            1,
            1,
            1,
            1,
            2,
            8,
            10,
            6,
            4,
            5,
            7,
            4,
            3,
            4,
            6,
            9,
            10,
            6,
            3,
            2,
            1,
            1,
        ]
        hour = rng.choices(range(24), weights=hour_weights, k=1)[0]
        candidate = datetime.combine(
            candidate_day,
            datetime.min.time(),
            tzinfo=timezone.utc,
        ) + timedelta(
            hours=hour,
            minutes=rng.randrange(60),
            seconds=rng.randrange(60),
        )
        weekday_weight = 0.85 if candidate.weekday() < 5 else 0.35
        if candidate <= now and rng.random() <= weekday_weight:
            return candidate
    return now - timedelta(seconds=rng.randrange(max(1, days * 86400)))


def generate_event_rows(
    persons: list[dict],
    cameras: list[dict],
    event_count: int,
    days: int,
    *,
    seed: int = 42,
    now: datetime | None = None,
) -> tuple[list[dict], list[dict]]:
    if not persons or not cameras:
        raise ValueError("生成事件前必须至少有一名人员和一个摄像头")
    if event_count < 0 or days <= 0:
        raise ValueError("event_count 必须非负且 days 必须大于 0")

    rng = random.Random(seed)
    current = now or datetime.now(timezone.utc)
    person_weights = [1 / (index + 1) ** 0.65 for index in range(len(persons))]
    camera_weights = [5, 3.5, 4.5, 2.5, 3][: len(cameras)]
    if len(camera_weights) < len(cameras):
        camera_weights.extend([1.5] * (len(cameras) - len(camera_weights)))

    face_rows = []
    unknown_rows = []
    for index in range(event_count):
        event_id = uuid.UUID(int=rng.getrandbits(128), version=4)
        event_time = _weighted_event_time(rng, current, days)
        camera = rng.choices(cameras, weights=camera_weights, k=1)[0]
        is_known = rng.random() < 0.85

        if is_known:
            person = rng.choices(persons, weights=person_weights, k=1)[0]
            confidence = min(0.99, max(0.65, rng.betavariate(8, 2)))
            person_id = person["id"]
            person_name = person["name"]
            event_type = "known"
        else:
            confidence = min(0.60, max(0.15, rng.betavariate(2, 5)))
            person_id = None
            person_name = None
            event_type = "unknown"

        face_rows.append(
            {
                "event_id": event_id,
                "person_id": person_id,
                "person_name": person_name,
                "camera_id": camera["id"],
                "camera_name": camera["name"],
                "event_time": event_time,
                "confidence_score": round(confidence, 4),
                "event_type": event_type,
                "snapshot_path": str(
                    Path("snapshots")
                    / event_time.strftime("%Y/%m/%d")
                    / f"{event_id}.jpg"
                ).replace("\\", "/"),
                "created_at": current,
            }
        )

        if not is_known:
            duration = rng.randrange(0, 31)
            unknown_rows.append(
                {
                    "event_id": event_id,
                    "track_id": f"TRACK-{event_time:%Y%m%d}-{index:06d}",
                    "first_seen_at": event_time,
                    "last_seen_at": event_time + timedelta(seconds=duration),
                    "occurrence_count": rng.randint(1, 8),
                    "notes": None,
                    "created_at": current,
                }
            )
    return face_rows, unknown_rows


def _batched(rows: list[dict], batch_size: int):
    for start in range(0, len(rows), batch_size):
        yield rows[start : start + batch_size]


def seed_database(
    persons_count: int = 20,
    cameras_count: int = 5,
    events_count: int = 100_000,
    days: int = 90,
    *,
    seed: int = 42,
    reset: bool = True,
    batch_size: int = 5000,
) -> dict:
    with SessionLocal() as db:
        if reset:
            db.execute(delete(UnknownEvent))
            db.execute(delete(FaceEvent))
            db.execute(delete(Camera))
            db.execute(delete(Person))
            db.commit()

        existing_persons = db.query(Person).count()
        existing_cameras = db.query(Camera).count()
        if existing_persons == 0:
            db.execute(insert(Person), build_person_rows(persons_count))
        if existing_cameras == 0:
            db.execute(insert(Camera), build_camera_rows(cameras_count))
        db.commit()

        persons = [
            {"id": person.id, "name": person.name}
            for person in db.query(Person).order_by(Person.id).all()
        ]
        cameras = [
            {"id": camera.id, "name": camera.name}
            for camera in db.query(Camera).order_by(Camera.id).all()
        ]
        face_rows, unknown_rows = generate_event_rows(
            persons,
            cameras,
            events_count,
            days,
            seed=seed,
        )
        for batch in _batched(face_rows, batch_size):
            db.execute(insert(FaceEvent), batch)
        for batch in _batched(unknown_rows, batch_size):
            db.execute(insert(UnknownEvent), batch)
        db.commit()

    return {
        "persons": len(persons),
        "cameras": len(cameras),
        "events": len(face_rows),
        "unknown_events": len(unknown_rows),
    }


def parse_args():
    parser = argparse.ArgumentParser(description="生成事件中心模拟数据")
    parser.add_argument("--persons", type=int, default=20)
    parser.add_argument("--cameras", type=int, default=5)
    parser.add_argument("--events", type=int, default=100_000)
    parser.add_argument("--days", type=int, default=90)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--batch-size", type=int, default=5000)
    parser.add_argument("--no-reset", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    result = seed_database(
        persons_count=args.persons,
        cameras_count=args.cameras,
        events_count=args.events,
        days=args.days,
        seed=args.seed,
        reset=not args.no_reset,
        batch_size=args.batch_size,
    )
    print(result)


if __name__ == "__main__":
    main()
