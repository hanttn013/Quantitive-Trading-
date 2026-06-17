from app.engines.data.fixtures import xauusd_m5_fixture
from app.engines.data.validation import validate_market_bars


def test_xauusd_fixture_is_valid_and_deterministic():
    bars = xauusd_m5_fixture(10)
    report = validate_market_bars(bars)

    assert len(bars) == 10
    assert report["status"] == "VALID"
    assert bars[0]["timestamp"] < bars[-1]["timestamp"]


def test_validator_rejects_duplicate_invalid_ohlc_and_negative_spread():
    bars = xauusd_m5_fixture(2)
    bars[1]["timestamp"] = bars[0]["timestamp"]
    bars[1]["high"] = 1
    bars[1]["low"] = 2
    bars[1]["spread"] = -1

    report = validate_market_bars(bars)
    codes = {issue["code"] for issue in report["issues"]}

    assert report["status"] == "INVALID"
    assert {"DUPLICATE_TIMESTAMP", "HIGH_BELOW_LOW", "NEGATIVE_SPREAD"}.issubset(codes)

