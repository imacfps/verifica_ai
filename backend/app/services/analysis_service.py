"""Orquestra validação, inferência e (opcionalmente) log de metadados."""

import asyncio
import hashlib

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.detectors.base import Detector
from app.models.analysis_log import AnalysisLog
from app.schemas.analysis import AnalysisResult
from app.utils.image_validation import decode_image_safely, read_upload_safely

settings = get_settings()
logger = get_logger(__name__)


async def analyze_image(
    file: UploadFile,
    detector: Detector,
    db: AsyncSession | None = None,
) -> AnalysisResult:
    raw = await read_upload_safely(file)
    image = decode_image_safely(raw)

    # to_thread: detectores fazem inferência bloqueante (CPU/torch) ou
    # chamada de rede (LlmJudgeDetector) — sem isso, travariam a event loop
    # inteira (todas as outras requisições, inclusive /health) até terminar.
    prob_ai = await asyncio.to_thread(detector.predict, image)
    result = AnalysisResult(
        prob_ai=round(prob_ai, 4),
        prob_real=round(1.0 - prob_ai, 4),
        label="ai-generated" if prob_ai >= 0.5 else "real",
        model=detector.name,
    )

    if settings.ENABLE_ANALYSIS_LOGGING and db is not None:
        await _log_analysis(db, raw, result, detector.name)

    return result


async def _log_analysis(
    db: AsyncSession, raw: bytes, result: AnalysisResult, model_name: str
) -> None:
    entry = AnalysisLog(
        image_sha256=hashlib.sha256(raw).hexdigest(),
        prob_ai=result.prob_ai,
        label=result.label,
        model_name=model_name,
    )
    db.add(entry)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("Falha ao gravar log de análise; seguindo sem interromper a resposta.")
