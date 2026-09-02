"""Ponto único de instanciação do detector ativo (singleton por processo)."""

from functools import lru_cache

from app.core.config import get_settings
from app.core.logging import get_logger
from app.detectors.base import Detector
from app.detectors.mock import MockDetector

logger = get_logger(__name__)


def _load_gemini() -> Detector:
    from app.detectors.gemini import GeminiDetector

    return GeminiDetector(get_settings().GEMINI_MODEL_PATH)


def _load_hf() -> Detector:
    from app.detectors.huggingface import HuggingFaceDetector

    return HuggingFaceDetector()


@lru_cache(maxsize=1)
def get_detector() -> Detector:
    settings = get_settings()
    mode = settings.DETECTOR_MODE

    if mode == "mock":
        return MockDetector()

    if mode == "gemini":
        return _load_gemini()

    if mode == "hf":
        return _load_hf()

    # "auto": modelo próprio (Gemini) > baseline HF > mock, na ordem de qualidade
    fallback_chain: list[tuple] = [
        (_load_gemini, (ImportError, FileNotFoundError)),
        (_load_hf, (ImportError,)),
    ]
    for loader, missing_dep_exc in fallback_chain:
        try:
            return loader()
        except missing_dep_exc as exc:
            logger.info(
                "Detector '%s' indisponível (%s); tentando o próximo.", loader.__name__, exc
            )

    logger.warning("Nenhum detector treinado disponível — usando MockDetector.")
    return MockDetector()
