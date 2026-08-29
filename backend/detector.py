"""
Camada de abstração do modelo detector.

Duas implementações:

1. HuggingFaceDetector — usa um classificador pré-treinado da Hugging Face
   (ViT fine-tunado para detecção de imagens sintéticas). Baixa ~350 MB na
   primeira execução. Bom o suficiente para demonstração; a precisão não é
   o foco nesta fase.

2. MockDetector — retorna uma pseudo-probabilidade determinística derivada
   dos bytes da imagem. Serve para desenvolver e demonstrar o fluxo completo
   (site → API → resposta) sem depender de download de modelo ou GPU.

Controle via variável de ambiente:
    DETECTOR_MODE=mock  -> força o mock
    DETECTOR_MODE=hf    -> força o modelo real (padrão se transformers instalado)

Para a fase final do TCC, substitua/adicione aqui uma classe que carregue o
modelo treinado do zero (ex.: pesos .pt do PyTorch) mantendo a interface
`predict(image) -> float`.
"""

import hashlib
import os
from functools import lru_cache

from PIL import Image

# Modelo pré-treinado de detecção de imagens sintéticas (ViT).
# Alternativas: "Organika/sdxl-detector", "dima806/ai_vs_real_image_detection"
HF_MODEL_ID = "umm-maybe/AI-image-detector"


class MockDetector:
    """Detector falso para desenvolvimento — NÃO usa IA de verdade."""

    name = "mock-v0 (desenvolvimento)"
    is_mock = True

    def predict(self, image: Image.Image) -> float:
        # Hash dos pixels -> número estável em [0, 1].
        # A mesma imagem sempre retorna a mesma "probabilidade".
        digest = hashlib.sha256(image.tobytes()[:65536]).digest()
        return int.from_bytes(digest[:4], "big") / 0xFFFFFFFF


class HuggingFaceDetector:
    """Detector real usando pipeline de classificação de imagens da HF."""

    name = HF_MODEL_ID
    is_mock = False

    # Rótulos que cada modelo usa para a classe "gerada por IA"
    AI_LABELS = {"artificial", "ai", "fake", "ai_gen", "artificial_image"}

    def __init__(self):
        from transformers import pipeline  # import tardio: só se necessário

        self._pipe = pipeline("image-classification", model=HF_MODEL_ID)

    def predict(self, image: Image.Image) -> float:
        results = self._pipe(image)
        # results: [{"label": "artificial", "score": 0.91}, {"label": "human", ...}]
        for r in results:
            if r["label"].lower() in self.AI_LABELS:
                return float(r["score"])
        # Se nenhum rótulo "IA" for encontrado, assume complemento do primeiro
        return 1.0 - float(results[0]["score"])


@lru_cache(maxsize=1)
def get_detector():
    """Instancia o detector uma única vez (singleton via lru_cache)."""
    mode = os.getenv("DETECTOR_MODE", "").lower()

    if mode == "mock":
        return MockDetector()

    if mode == "hf":
        return HuggingFaceDetector()

    # Automático: usa o modelo real se transformers estiver instalado
    try:
        return HuggingFaceDetector()
    except ImportError:
        print("[detector] transformers não instalado — usando MockDetector.")
        return MockDetector()
