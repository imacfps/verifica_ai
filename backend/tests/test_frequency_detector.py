import numpy as np
from PIL import Image

from app.detectors.frequency import FrequencyDetector


def test_predict_returns_probability_in_range():
    detector = FrequencyDetector()
    image = Image.new("RGB", (64, 64), (30, 60, 90))
    prob = detector.predict(image)
    assert 0.0 <= prob <= 1.0


def test_periodic_grid_pattern_scores_higher_than_natural_texture():
    detector = FrequencyDetector()

    x = np.arange(256)
    grid = (128 + 100 * np.sin(x * 0.9)).astype("uint8")
    grid_image = Image.fromarray(np.tile(grid, (256, 1)))

    rng = np.random.default_rng(0)
    texture = np.zeros((256, 256))
    yy, xx = np.mgrid[0:256, 0:256]
    for k in range(1, 6):
        fx, fy = rng.uniform(0.5, 3, 2)
        phase = rng.uniform(0, 2 * np.pi)
        texture += np.sin(2 * np.pi * (fx * xx / 256 + fy * yy / 256) + phase) / k
    texture = (texture - texture.min()) / (texture.max() - texture.min()) * 255
    texture_image = Image.fromarray(texture.astype("uint8"))

    assert detector.predict(grid_image) > detector.predict(texture_image)


def test_pure_noise_scores_low():
    detector = FrequencyDetector()
    rng = np.random.default_rng(1)
    noise = Image.fromarray(rng.integers(0, 255, (128, 128), dtype="uint8"))
    assert detector.predict(noise) < 0.3
