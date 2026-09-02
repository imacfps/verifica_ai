"""Métricas de classificação binária compartilhadas entre treino e avaliação."""

from dataclasses import dataclass

from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


@dataclass
class ClassificationMetrics:
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float | None  # None quando o batch/lote não tem as duas classes
    brier: float
    ece: float

    def as_dict(self) -> dict:
        return {
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1": self.f1,
            "roc_auc": self.roc_auc,
            "brier": self.brier,
            "ece": self.ece,
        }


def expected_calibration_error(
    y_true: list[float], y_prob: list[float], n_bins: int = 10
) -> float:
    """Diferença média (ponderada por tamanho do bin) entre confiança prevista e
    acerto observado — mede se `prob_ai` é utilizável como probabilidade, não só
    se o rótulo derivado dela está certo. Ver docs/dataset.md (calibração)."""
    bin_edges = [i / n_bins for i in range(n_bins + 1)]
    n = len(y_prob)
    ece = 0.0
    for lo, hi in zip(bin_edges[:-1], bin_edges[1:], strict=True):
        in_bin = [
            (p, t)
            for p, t in zip(y_prob, y_true, strict=True)
            if (p > lo or (lo == 0 and p == 0)) and p <= hi
        ]
        if not in_bin:
            continue
        bin_probs = [p for p, _ in in_bin]
        bin_targets = [t for _, t in in_bin]
        confidence = sum(bin_probs) / len(bin_probs)
        accuracy = sum(bin_targets) / len(bin_targets)
        ece += (len(in_bin) / n) * abs(confidence - accuracy)
    return ece


def compute_metrics(
    y_true: list[float], y_prob: list[float], threshold: float = 0.5
) -> ClassificationMetrics:
    y_pred = [1 if p >= threshold else 0 for p in y_prob]

    try:
        auc = roc_auc_score(y_true, y_prob)
    except ValueError:
        auc = None  # só uma classe presente no conjunto avaliado

    return ClassificationMetrics(
        accuracy=accuracy_score(y_true, y_pred),
        precision=precision_score(y_true, y_pred, zero_division=0),
        recall=recall_score(y_true, y_pred, zero_division=0),
        f1=f1_score(y_true, y_pred, zero_division=0),
        roc_auc=auc,
        brier=brier_score_loss(y_true, y_prob),
        ece=expected_calibration_error(y_true, y_prob),
    )
