"""Scaffold do banco de imagens consolidado (Fase 2 do TCC).

Este modelo já define o schema para o dataset usado no treinamento e
avaliação do detector focado no gerador do Gemini, mas ainda não possui
endpoints de ingestão expostos — é o "ponto de extensão" para quando a
etapa de curadoria de dataset começar. Imagens reais nunca ficam no banco
relacional: `storage_path` aponta para um object storage (ex.: MinIO/S3)
mantido fora do Postgres.
"""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ImageLabel(StrEnum):
    REAL = "real"
    AI_GENERATED = "ai_generated"


class DatasetSplit(StrEnum):
    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"


class DatasetImage(Base):
    __tablename__ = "dataset_images"
    __table_args__ = (UniqueConstraint("sha256", name="uq_dataset_images_sha256"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    label: Mapped[ImageLabel] = mapped_column(Enum(ImageLabel, name="image_label"))
    # Gerador de origem quando label=ai_generated: "gemini-2", "imagen-3", "nano-banana", etc.
    # Nulo para imagens reais.
    generator: Mapped[str | None] = mapped_column(String(60), nullable=True)
    split: Mapped[DatasetSplit] = mapped_column(
        Enum(DatasetSplit, name="dataset_split"), default=DatasetSplit.TRAIN
    )
    storage_path: Mapped[str] = mapped_column(String(500))
    source_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
