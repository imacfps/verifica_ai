"""Contrato que todo detector precisa cumprir.

Trocar o modelo (ex.: modelo próprio treinado do zero para detecção
específica de imagens geradas pelo Gemini) significa apenas implementar
esta interface e registrá-la em `registry.get_detector()` — nada em
`api/` ou `services/` precisa mudar.
"""

from typing import Protocol

from PIL import Image


class Detector(Protocol):
    name: str
    is_mock: bool

    def predict(self, image: Image.Image) -> float:
        """Retorna a probabilidade estimada [0, 1] de a imagem ser gerada por IA."""
        ...
