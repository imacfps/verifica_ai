"""API pública para terceiros — distinta do uso interno (site/extensão).

Mesma lógica de análise de `analyze.py`, mas exige uma API key
(`X-API-Key`, ver `app/api/deps.py::get_api_client`) e tem cota própria por
cliente, não por IP. CORS não é relevante aqui: é um mecanismo de
enforcement do navegador, não bloqueia chamadas servidor-a-servidor — um
cliente terceiro não precisa (nem deve) estar em `ALLOWED_EXTENSION_ORIGINS`
ou `CORS_ORIGINS`. Ver `docs/public_api.md`.
"""

from fastapi import APIRouter, Depends, File, Request, UploadFile
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_api_client, get_current_detector, get_db
from app.core.config import get_settings
from app.core.security import limiter
from app.detectors.base import Detector
from app.models.api_client import ApiClient
from app.schemas.analysis import AnalysisResult
from app.services.analysis_service import analyze_image

router = APIRouter()
settings = get_settings()


def _api_key_rate_limit_key(request: Request) -> str:
    # A chave de rate limit é o próprio valor do header — cada cliente tem
    # cota independente. Sem header (não deveria chegar aqui, get_api_client
    # já barra antes), cai pro IP como nos demais endpoints.
    return request.headers.get("x-api-key") or get_remote_address(request)


@router.post("/public/analyze", response_model=AnalysisResult)
@limiter.limit(settings.RATE_LIMIT_PUBLIC_API, key_func=_api_key_rate_limit_key)
async def public_analyze(
    request: Request,
    file: UploadFile = File(...),
    detector: Detector = Depends(get_current_detector),
    db: AsyncSession = Depends(get_db),
    client: ApiClient = Depends(get_api_client),
) -> AnalysisResult:
    """Mesmo contrato de `POST /v1/analyze`, autenticado por API key."""
    return await analyze_image(file=file, detector=detector, db=db)
