"""create event center tables

Revision ID: 0001
Revises:
Create Date: 2026-06-06
"""

from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "persons",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("external_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("gender", sa.String(20)),
        sa.Column("department", sa.String(100)),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_persons"),
        sa.UniqueConstraint("external_id", name="uq_persons_external_id"),
    )
    op.create_index("ix_persons_name", "persons", ["name"])
    op.create_index("ix_persons_department", "persons", ["department"])
    op.create_index("ix_persons_status", "persons", ["status"])

    op.create_table(
        "cameras",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("location", sa.String(255)),
        sa.Column("latitude", sa.Numeric(9, 6)),
        sa.Column("longitude", sa.Numeric(9, 6)),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_cameras"),
        sa.UniqueConstraint("code", name="uq_cameras_code"),
    )
    op.create_index("ix_cameras_name", "cameras", ["name"])
    op.create_index("ix_cameras_location", "cameras", ["location"])
    op.create_index("ix_cameras_status", "cameras", ["status"])

    op.create_table(
        "face_events",
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("person_id", sa.BigInteger()),
        sa.Column("person_name", sa.String(100)),
        sa.Column("camera_id", sa.BigInteger()),
        sa.Column("camera_name", sa.String(100), nullable=False),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("confidence_score", sa.Numeric(5, 4), nullable=False),
        sa.Column("event_type", sa.String(16), nullable=False),
        sa.Column("snapshot_path", sa.String(500)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "confidence_score >= 0 AND confidence_score <= 1",
            name="confidence_range",
        ),
        sa.CheckConstraint(
            "(event_type = 'known' AND person_name IS NOT NULL) "
            "OR (event_type = 'unknown' AND person_id IS NULL AND person_name IS NULL)",
            name="person_consistency",
        ),
        sa.CheckConstraint(
            "event_type IN ('known', 'unknown')",
            name="event_type",
        ),
        sa.ForeignKeyConstraint(
            ["person_id"], ["persons.id"], ondelete="SET NULL", name="fk_events_person"
        ),
        sa.ForeignKeyConstraint(
            ["camera_id"], ["cameras.id"], ondelete="SET NULL", name="fk_events_camera"
        ),
        sa.PrimaryKeyConstraint("event_id", name="pk_face_events"),
    )
    op.create_index("ix_face_events_event_time", "face_events", ["event_time"])
    op.create_index(
        "ix_face_events_person_time", "face_events", ["person_id", "event_time"]
    )
    op.create_index(
        "ix_face_events_camera_time", "face_events", ["camera_id", "event_time"]
    )
    op.create_index(
        "ix_face_events_type_time", "face_events", ["event_type", "event_time"]
    )
    op.create_index("ix_face_events_created_at", "face_events", ["created_at"])

    op.create_table(
        "unknown_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("track_id", sa.String(100)),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("occurrence_count", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "occurrence_count > 0", name="occurrence_positive"
        ),
        sa.CheckConstraint(
            "last_seen_at >= first_seen_at", name="seen_order"
        ),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["face_events.event_id"],
            ondelete="CASCADE",
            name="fk_unknown_events_event",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_unknown_events"),
        sa.UniqueConstraint("event_id", name="uq_unknown_events_event_id"),
    )


def downgrade():
    op.drop_table("unknown_events")
    op.drop_index("ix_face_events_created_at", table_name="face_events")
    op.drop_index("ix_face_events_type_time", table_name="face_events")
    op.drop_index("ix_face_events_camera_time", table_name="face_events")
    op.drop_index("ix_face_events_person_time", table_name="face_events")
    op.drop_index("ix_face_events_event_time", table_name="face_events")
    op.drop_table("face_events")
    op.drop_index("ix_cameras_status", table_name="cameras")
    op.drop_index("ix_cameras_location", table_name="cameras")
    op.drop_index("ix_cameras_name", table_name="cameras")
    op.drop_table("cameras")
    op.drop_index("ix_persons_status", table_name="persons")
    op.drop_index("ix_persons_department", table_name="persons")
    op.drop_index("ix_persons_name", table_name="persons")
    op.drop_table("persons")
