import pytest
from PIL import Image

from app.detectors.ensemble import EnsembleDetector
from app.detectors.llm_judge import LlmJudgeDetector


def test_ensemble_always_includes_frequency_signal():
    detector = EnsembleDetector()
    assert "frequency" in detector.name
    assert detector.is_mock is False


def test_ensemble_predict_returns_probability_in_range():
    detector = EnsembleDetector()
    image = Image.new("RGB", (64, 64), (10, 200, 90))
    prob = detector.predict(image)
    assert 0.0 <= prob <= 1.0


def test_ensemble_survives_a_signal_raising_at_predict_time(monkeypatch):
    detector = EnsembleDetector()

    def boom(self, image):
        raise RuntimeError("sinal indisponível no momento")

    monkeypatch.setattr(type(detector._signals[0]), "predict", boom)

    image = Image.new("RGB", (32, 32), (0, 0, 0))
    # Não deve levantar — só exclui o sinal que falhou, a menos que TODOS falhem.
    prob = detector.predict(image)
    assert 0.0 <= prob <= 1.0


def test_llm_judge_detector_requires_api_key(monkeypatch):
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "GEMINI_API_KEY", None)
    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        LlmJudgeDetector()
