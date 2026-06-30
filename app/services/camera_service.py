from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Camera
from app.schemas.camera import CameraCreate
from app.services.exceptions import ConflictError


def create_camera(db: Session, payload: CameraCreate) -> Camera:
    camera = Camera(**payload.model_dump())
    db.add(camera)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(f"摄像头 code 已存在: {payload.code}") from exc
    db.refresh(camera)
    return camera
