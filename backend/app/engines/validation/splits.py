from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeSplit:
    train: tuple[int, int]
    validation: tuple[int, int]
    test: tuple[int, int]


def train_validation_test_split(length: int, train_pct: float, validation_pct: float) -> TimeSplit:
    if length < 3:
        raise ValueError("time series needs at least 3 rows")
    if not 0 < train_pct < 1 or not 0 < validation_pct < 1 or train_pct + validation_pct >= 1:
        raise ValueError("invalid split percentages")
    train_end = int(length * train_pct)
    validation_end = train_end + int(length * validation_pct)
    if train_end <= 0 or validation_end <= train_end or validation_end >= length:
        raise ValueError("split would create an empty segment")
    return TimeSplit(train=(0, train_end), validation=(train_end, validation_end), test=(validation_end, length))


def walk_forward_folds(
    length: int,
    *,
    train_size: int,
    validation_size: int,
    test_size: int,
    step_size: int,
    anchored: bool = True,
) -> list[TimeSplit]:
    if min(train_size, validation_size, test_size, step_size) <= 0:
        raise ValueError("fold sizes must be positive")
    folds: list[TimeSplit] = []
    start = 0
    while True:
        train_start = 0 if anchored else start
        train_end = start + train_size
        validation_end = train_end + validation_size
        test_end = validation_end + test_size
        if test_end > length:
            break
        folds.append(TimeSplit((train_start, train_end), (train_end, validation_end), (validation_end, test_end)))
        start += step_size
    return folds
