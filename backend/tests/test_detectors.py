from PIL import Image

from app.detectors.mock import MockDetector


def test_mock_detector_is_deterministic():
    detector = MockDetector()
    image = Image.new("RGB", (16, 16), (5, 5, 5))
    assert detector.predict(image) == detector.predict(image)


def test_mock_detector_returns_probability_range():
    detector = MockDetector()
    image = Image.new("RGB", (16, 16), (200, 100, 50))
    prob = detector.predict(image)
    assert 0.0 <= prob <= 1.0
