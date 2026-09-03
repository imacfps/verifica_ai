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


def _load_frequency() -> Detector:
    from app.detectors.frequency import FrequencyDetector

    return FrequencyDetector()


def _load_llm_judge() -> Detector:
    from app.detectors.llm_judge import LlmJudgeDetector

    return LlmJudgeDetector()


def _load_ensemble() -> Detector:
    from app.detectors.ensemble import EnsembleDetector

    return EnsembleDetector()


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

    if mode == "frequency":
        return _load_frequency()

    if mode == "llm_judge":
        return _load_llm_judge()

    if mode == "ensemble":
        return _load_ensemble()

    # "auto": modelo próprio (Gemini, se treinado) > ensemble (sinais sem
    # dataset próprio) > mock. O ensemble já inclui o baseline HF quando
    # disponível, então não há mais um salto isolado pra "hf" sozinho aqui.
    fallback_chain: list[tuple] = [
        (_load_gemini, (ImportError, FileNotFoundError)),
        (_load_ensemble, (ImportError,)),
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
