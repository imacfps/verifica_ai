from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_detector, get_db
from app.core.config import get_settings
from app.core.security import limiter
from app.detectors.base import Detector
from app.schemas.analysis import AnalysisResult
from app.services.analysis_service import analyze_image

router = APIRouter()
settings = get_settings()


@router.post("/analyze", response_model=AnalysisResult)
@limiter.limit(settings.RATE_LIMIT_ANALYZE)
async def analyze(
    request: Request,
    file: UploadFile = File(...),
    detector: Detector = Depends(get_current_detector),
    db: AsyncSession = Depends(get_db),
) -> AnalysisResult:
    """Recebe uma imagem (multipart/form-data) e retorna a probabilidade de ser gerada por IA.

    A imagem é processada inteiramente em memória e descartada após a
    resposta — nada é persistido em disco (ver `docs/privacy.md`).
    """
    return await analyze_image(file=file, detector=detector, db=db)
