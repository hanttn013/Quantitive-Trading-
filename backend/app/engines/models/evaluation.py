from __future__ import annotations


def classification_metrics(y_true: list[str], y_pred: list[str], positive_label: str = "BUY_SETUP") -> dict[str, float]:
    if len(y_true) != len(y_pred):
        raise ValueError("label and prediction lengths differ")
    tp = sum(1 for true, pred in zip(y_true, y_pred, strict=True) if true == positive_label and pred == positive_label)
    fp = sum(1 for true, pred in zip(y_true, y_pred, strict=True) if true != positive_label and pred == positive_label)
    fn = sum(1 for true, pred in zip(y_true, y_pred, strict=True) if true == positive_label and pred != positive_label)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "support": float(len(y_true))}


def trading_validity_status(*, predictive_metrics: dict[str, float], expectancy: float) -> str:
    if predictive_metrics.get("f1", 0.0) >= 0.6 and expectancy <= 0:
        return "PREDICTIVELY_VALID/TRADING_INVALID"
    if predictive_metrics.get("f1", 0.0) >= 0.6 and expectancy > 0:
        return "TRADING_VALID"
    return "PREDICTIVELY_INVALID"
