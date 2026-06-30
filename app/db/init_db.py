from app.db.base import Base


def init_db() -> None:
    import app.models  # noqa: F401
    import app.db.session as session_module

    Base.metadata.create_all(bind=session_module.engine)
