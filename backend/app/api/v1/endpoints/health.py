from fastapi import APIRouter, Depends

from app.api.deps import get_current_detector
from app.detectors.base import Detector
from app.schemas.analysis import HealthStatus

router = APIRouter()


@router.get("/health", response_model=HealthStatus)
def health(detector: Detector = Depends(get_current_detector)) -> HealthStatus:
    """Verificação de disponibilidade — útil para a extensão de navegador."""
    return HealthStatus(status="ok", model=detector.name, mock=detector.is_mock)
