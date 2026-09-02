"""initial schema — analysis_logs e dataset_images

Revision ID: 0001
Revises:
Create Date: 2026-08-31
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "analysis_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("image_sha256", sa.String(length=64), nullable=False),
        sa.Column("prob_ai", sa.Float(), nullable=False),
        sa.Column("label", sa.String(length=20), nullable=False),
        sa.Column("model_name", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_analysis_logs_image_sha256", "analysis_logs", ["image_sha256"])

    image_label = postgresql.ENUM("real", "ai_generated", name="image_label")
    dataset_split = postgresql.ENUM("train", "validation", "test", name="dataset_split")
    image_label.create(op.get_bind(), checkfirst=True)
    dataset_split.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "dataset_images",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("label", image_label, nullable=False),
        sa.Column("generator", sa.String(length=60), nullable=True),
        sa.Column("split", dataset_split, nullable=False, server_default="train"),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column("source_note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("sha256", name="uq_dataset_images_sha256"),
    )
    op.create_index("ix_dataset_images_sha256", "dataset_images", ["sha256"])


def downgrade() -> None:
    op.drop_index("ix_dataset_images_sha256", table_name="dataset_images")
    op.drop_table("dataset_images")
    postgresql.ENUM(name="dataset_split").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="image_label").drop(op.get_bind(), checkfirst=True)

    op.drop_index("ix_analysis_logs_image_sha256", table_name="analysis_logs")
    op.drop_table("analysis_logs")
