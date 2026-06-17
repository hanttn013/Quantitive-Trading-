from app.engines.data.fixtures import xauusd_m5_fixture
from app.engines.features import add_core_features
from app.engines.strategies import StrategyContext, XauUsdM5MeanReversionStrategy, label_liquidity_sweep, label_regime


def test_mean_reversion_strategy_can_emit_buy_signal_from_features():
    row = add_core_features(xauusd_m5_fixture(30))[-1]
    row.update({"close": row["bb_lower"] - 0.1, "rsi": 25, "zscore": -2.0, "wick_bottom_ratio": 0.4})

    signal = XauUsdM5MeanReversionStrategy().evaluate(row, StrategyContext())

    assert signal.action == "BUY"
    assert signal.stop_loss is not None
    assert signal.take_profit is not None


def test_mean_reversion_blocks_uncertain_regime():
    row = add_core_features(xauusd_m5_fixture(30))[-1]

    signal = XauUsdM5MeanReversionStrategy().evaluate(row, StrategyContext(regime="UNCERTAIN"))

    assert signal.action == "NO_TRADE"
    assert signal.reason["blocked"] == "REGIME"


def test_hmm_low_confidence_is_uncertain():
    label, confidence = label_regime({"volatility": 0.5, "trend_strength": 0.1}, confidence=0.4)

    assert label == "UNCERTAIN"
    assert confidence == 0.4


def test_liquidity_sweep_label_uses_future_horizon_order():
    assert label_liquidity_sweep([101, 103], entry=100, take_profit=102, stop_loss=98) == "positive"
    assert label_liquidity_sweep([99, 97, 103], entry=100, take_profit=102, stop_loss=98) == "negative"
    assert label_liquidity_sweep([100.5, 100.2], entry=100, take_profit=102, stop_loss=98) == "neutral"
