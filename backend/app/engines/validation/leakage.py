from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LeakageResult:
    valid: bool
    issues: list[str]


def check_leakage(config: dict[str, object]) -> LeakageResult:
    issues: list[str] = []
    if config.get("random_split") or config.get("shuffle"):
        issues.append("RANDOM_TIME_SERIES_SPLIT")
    if config.get("scaler_fit_scope") not in {None, "train"}:
        issues.append("SCALER_FIT_OUTSIDE_TRAIN")
    for feature in config.get("features", []) or []:
        if isinstance(feature, dict) and int(feature.get("shift", 0)) < 0:
            issues.append(f"FUTURE_FEATURE:{feature.get('name', 'unknown')}")
    if config.get("full_series_preprocessing"):
        issues.append("FULL_SERIES_PREPROCESSING")
    if config.get("label_crosses_split_boundary"):
        issues.append("LABEL_OVERLAP_SPLIT_BOUNDARY")
    return LeakageResult(valid=not issues, issues=issues)
