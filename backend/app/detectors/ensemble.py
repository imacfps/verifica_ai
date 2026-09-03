"""Combina múltiplos sinais de detecção sem exigir dataset rotulado próprio.

Cada sub-sinal é independente e não-treinado (ou pré-treinado por terceiros):
análise espectral (`FrequencyDetector`, sempre disponível), o baseline HF
(`HuggingFaceDetector`, se `transformers` estiver instalado) e um juiz
multimodal via API do Gemini (`LlmJudgeDetector`, se `GEMINI_API_KEY`
estiver configurada). Um sinal indisponível é simplesmente pulado — tanto na
construção (dependência ausente) quanto em tempo de execução (ex.: a API do
Gemini fora do ar não derruba a análise, só reduz o ensemble aos sinais
restantes).

A combinação é uma média simples — não há pesos ajustados, porque não existe
ainda um conjunto de validação rotulado pra ajustá-los (ver docs/dataset.md).
Isso é uma decisão deliberada: melhor um baseline honesto e documentado do
que pesos inventados sem dado nenhum por trás. Recalibrar (ex.: regressão
logística sobre os sub-scores) é trabalho futuro assim que houver um
conjunto de validação, ainda que pequeno.
"""

from PIL import Image

from app.core.logging import get_logger
from app.detectors.base import Detector
from app.detectors.frequency import FrequencyDetector

logger = get_logger(__name__)


def _load_hf() -> Detector:
    from app.detectors.huggingface import HuggingFaceDetector

    return HuggingFaceDetector()


def _load_llm_judge() -> Detector:
    from app.detectors.llm_judge import LlmJudgeDetector

    return LlmJudgeDetector()


class EnsembleDetector:
    is_mock = False

    def __init__(self):
        self._signals: list[Detector] = [FrequencyDetector()]

        for loader, missing_dep_exc in (
            (_load_hf, (ImportError,)),
            (_load_llm_judge, (ImportError, ValueError)),
        ):
            try:
                self._signals.append(loader())
            except missing_dep_exc as exc:
                logger.info("Sinal do ensemble indisponível (%s); seguindo sem ele.", exc)

        signal_names = "+".join(_short_name(s) for s in self._signals)
        self.name = f"ensemble({signal_names})"

    def predict(self, image: Image.Image) -> float:
        scores: list[float] = []
        for signal in self._signals:
            try:
                scores.append(signal.predict(image))
            except Exception:
                logger.exception(
                    "Sinal '%s' falhou em tempo de execução; excluído desta análise.",
                    signal.name,
                )

        if not scores:
            raise RuntimeError("Nenhum sinal do ensemble conseguiu produzir uma predição.")

        return sum(scores) / len(scores)


def _short_name(detector: Detector) -> str:
    if isinstance(detector, FrequencyDetector):
        return "frequency"
    return "llm_judge" if "llm-judge" in detector.name else "hf"
