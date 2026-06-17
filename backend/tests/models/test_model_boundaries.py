import pytest

from backend.app.engines.models import assert_rl_action_requires_risk, classification_metrics, default_rl_schemas, trading_validity_status


def test_classifier_can_be_predictive_but_trading_invalid():
    metrics = classification_metrics(["BUY_SETUP", "BUY_SETUP", "NO_TRADE"], ["BUY_SETUP", "BUY_SETUP", "BUY_SETUP"])
    assert metrics["recall"] == 1.0
    assert trading_validity_status(predictive_metrics=metrics, expectancy=-1.0) == "PREDICTIVELY_VALID/TRADING_INVALID"


def test_rl_schema_cannot_bypass_risk_engine():
    schemas = default_rl_schemas()
    assert_rl_action_requires_risk(schemas["action"])
    with pytest.raises(PermissionError):
        assert_rl_action_requires_risk({"enum": ["BUY"], "requires_risk_decision": False})
