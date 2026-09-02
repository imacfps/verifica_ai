"""Log opcional (ENABLE_ANALYSIS_LOGGING) de metadados de análise.

Por padrão a aplicação NÃO persiste nada: a imagem enviada é processada em
memória e descartada após a resposta. Quando o log é habilitado, apenas o
hash sha256 da imagem e o resultado são gravados — nunca os bytes originais,
IP ou qualquer identificador do usuário (ver decisão de privacidade no
README).
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AnalysisLog(Base):
    __tablename__ = "analysis_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    image_sha256: Mapped[str] = mapped_column(String(64), index=True)
    prob_ai: Mapped[float] = mapped_column(Float)
    label: Mapped[str] = mapped_column(String(20))
    model_name: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
