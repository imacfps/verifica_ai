"""Métricas de classificação binária compartilhadas entre treino e avaliação."""

from dataclasses import dataclass

from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score


@dataclass
class ClassificationMetrics:
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float | None  # None quando o batch/lote não tem as duas classes

    def as_dict(self) -> dict:
        return {
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1": self.f1,
            "roc_auc": self.roc_auc,
        }


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
    )
