from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Person
from app.schemas.person import PersonCreate
from app.services.exceptions import ConflictError


def create_person(db: Session, payload: PersonCreate) -> Person:
    person = Person(**payload.model_dump())
    db.add(person)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(f"人员 external_id 已存在: {payload.external_id}") from exc
    db.refresh(person)
    return person
