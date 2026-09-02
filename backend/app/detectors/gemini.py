"""Detector próprio (Fase 2) — carrega um checkpoint treinado localmente.

Ver `training/README.md` para como gerar o checkpoint a partir do banco de
imagens consolidado (`docs/dataset.md`).
"""

from pathlib import Path

import torch
from PIL import Image

from app.detectors.gemini_model import PREPROCESS, GeminiDetectorModel


class GeminiDetector:
    name = "gemini-detector-v1"
    is_mock = False

    def __init__(self, checkpoint_path: str | Path):
        path = Path(checkpoint_path)
        if not path.is_file():
            raise FileNotFoundError(
                f"Checkpoint do GeminiDetector não encontrado em '{path}'. "
                "Treine o modelo (ver backend/training/README.md) ou use "
                "DETECTOR_MODE=mock / DETECTOR_MODE=hf enquanto isso."
            )

        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._model = GeminiDetectorModel(pretrained=False).to(self._device)

        # weights_only=True restringe o unpickling a tensores/tipos básicos —
        # mitiga execução de código arbitrário caso o arquivo de checkpoint
        # seja substituído por um pickle malicioso.
        checkpoint = torch.load(path, map_location=self._device, weights_only=True)
        self._model.load_state_dict(checkpoint["model_state"])
        self._model.eval()

    @torch.inference_mode()
    def predict(self, image: Image.Image) -> float:
        tensor = PREPROCESS(image).unsqueeze(0).to(self._device)
        logit = self._model(tensor)
        return torch.sigmoid(logit).item()
