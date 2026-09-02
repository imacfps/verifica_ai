"""Testes do detector próprio. `torch`/`torchvision` são deps opcionais
(requirements-train.txt) — se ausentes, os testes são pulados em vez de
quebrar o CI padrão da API.
"""

import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("torchvision")

from PIL import Image  # noqa: E402

from app.detectors.gemini import GeminiDetector  # noqa: E402
from app.detectors.gemini_model import GeminiDetectorModel  # noqa: E402


def test_model_forward_pass_returns_logit_per_image():
    model = GeminiDetectorModel(pretrained=False)
    model.eval()
    batch = torch.randn(2, 3, 224, 224)
    with torch.inference_mode():
        logits = model(batch)
    assert logits.shape == (2,)


def test_backbone_starts_frozen_and_can_be_unfrozen():
    model = GeminiDetectorModel(pretrained=False)
    assert all(not p.requires_grad for p in model.backbone.parameters())
    model.unfreeze_backbone()
    assert all(p.requires_grad for p in model.backbone.parameters())


def test_gemini_detector_missing_checkpoint_raises_clear_error(tmp_path):
    missing = tmp_path / "does-not-exist.pt"
    with pytest.raises(FileNotFoundError):
        GeminiDetector(missing)


def test_gemini_detector_predicts_probability_in_range(tmp_path):
    model = GeminiDetectorModel(pretrained=False)
    checkpoint_path = tmp_path / "checkpoint.pt"
    torch.save({"model_state": model.state_dict()}, checkpoint_path)

    detector = GeminiDetector(checkpoint_path)
    image = Image.new("RGB", (64, 64), (120, 80, 200))
    prob = detector.predict(image)

    assert 0.0 <= prob <= 1.0
