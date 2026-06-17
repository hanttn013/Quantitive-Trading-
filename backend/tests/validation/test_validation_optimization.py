from backend.app.engines.optimization import monte_carlo_sequence, stress_costs
from backend.app.engines.validation import check_leakage, train_validation_test_split, walk_forward_folds


def test_time_split_is_ordered_and_never_random():
    split = train_validation_test_split(100, 0.6, 0.2)
    assert split.train == (0, 60)
    assert split.validation == (60, 80)
    assert split.test == (80, 100)


def test_walk_forward_folds_do_not_overlap_wrongly():
    folds = walk_forward_folds(40, train_size=10, validation_size=5, test_size=5, step_size=5, anchored=False)
    assert folds[0].train == (0, 10)
    assert folds[0].validation == (10, 15)
    assert folds[0].test == (15, 20)
    assert folds[1].train == (5, 15)
    assert folds[1].validation[0] == folds[1].train[1]


def test_leakage_invalidates_future_features_and_full_series_scaler():
    result = check_leakage(
        {
            "shuffle": True,
            "scaler_fit_scope": "full",
            "features": [{"name": "future_return", "shift": -1}],
            "full_series_preprocessing": True,
        }
    )
    assert not result.valid
    assert "RANDOM_TIME_SERIES_SPLIT" in result.issues
    assert "SCALER_FIT_OUTSIDE_TRAIN" in result.issues
    assert "FUTURE_FEATURE:future_return" in result.issues


def test_cost_stress_and_monte_carlo_are_deterministic():
    stressed = stress_costs({"net_profit": 100.0, "spread_cost": 10.0, "slippage_cost": 5.0})
    assert stressed["stressed_net_profit"] == 85.0
    mc = monte_carlo_sequence([10, -20, 15], runs=10, seed=1, ruin_level=-25)
    assert mc["runs"] == 10.0
    assert 0.0 <= mc["probability_of_ruin"] <= 1.0
