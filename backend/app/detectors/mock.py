"""Detector determinístico para desenvolvimento — NÃO usa IA de verdade."""

import hashlib

from PIL import Image


class MockDetector:
    name = "mock-v0 (desenvolvimento)"
    is_mock = True

    def predict(self, image: Image.Image) -> float:
        digest = hashlib.sha256(image.tobytes()[:65536]).digest()
        return int.from_bytes(digest[:4], "big") / 0xFFFFFFFF
