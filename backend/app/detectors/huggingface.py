"""Detector real usando um classificador de imagens pré-treinado da Hugging Face.

Serve como baseline enquanto o modelo próprio (treinado para o gerador do
Gemini especificamente) não está pronto. Ver `docs/dataset.md` para o plano
do banco de imagens consolidado usado no treinamento final.
"""

from PIL import Image

from app.core.config import get_settings

settings = get_settings()

AI_LABELS = {"artificial", "ai", "fake", "ai_gen", "artificial_image"}


class HuggingFaceDetector:
    name = settings.HF_MODEL_ID
    is_mock = False

    def __init__(self):
        from transformers import pipeline  # import tardio: só se necessário

        self._pipe = pipeline("image-classification", model=settings.HF_MODEL_ID)

    def predict(self, image: Image.Image) -> float:
        results = self._pipe(image)
        for r in results:
            if r["label"].lower() in AI_LABELS:
                return float(r["score"])
        return 1.0 - float(results[0]["score"])
