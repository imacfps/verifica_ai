import math

from training.metrics import compute_metrics, expected_calibration_error


def test_perfectly_calibrated_predictions_have_zero_brier_and_ece():
    y_true = [1, 1, 0, 0]
    y_prob = [1.0, 1.0, 0.0, 0.0]

    metrics = compute_metrics(y_true, y_prob)

    assert metrics.accuracy == 1.0
    assert math.isclose(metrics.brier, 0.0, abs_tol=1e-9)
    assert math.isclose(metrics.ece, 0.0, abs_tol=1e-9)


def test_overconfident_wrong_predictions_are_penalized():
    y_true = [0, 0, 0, 0]
    y_prob = [0.9, 0.9, 0.9, 0.9]

    metrics = compute_metrics(y_true, y_prob)

    assert math.isclose(metrics.brier, 0.81, abs_tol=1e-9)
    assert math.isclose(metrics.ece, 0.9, abs_tol=1e-9)


def test_expected_calibration_error_ignores_empty_bins():
    # Só duas amostras, longe uma da outra — a maioria dos 10 bins fica vazia
    # e não deve contribuir (nem quebrar) o cálculo.
    ece = expected_calibration_error(y_true=[1, 0], y_prob=[0.95, 0.05])
    assert math.isclose(ece, 0.05, abs_tol=1e-9)
