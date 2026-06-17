from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class AppMetadata(TimestampMixin, Base):
    """Small persisted record proving DB setup before domain models land."""

    __tablename__ = "app_metadata"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value: Mapped[str] = mapped_column(String(512), nullable=False)


class Dataset(TimestampMixin, Base):
    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(16), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)
    versions: Mapped[list["DatasetVersion"]] = relationship(back_populates="dataset")


class DatasetVersion(TimestampMixin, Base):
    __tablename__ = "dataset_versions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    dataset_id: Mapped[str] = mapped_column(ForeignKey("datasets.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="DRAFT", nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    start_time: Mapped[str | None] = mapped_column(String(64))
    end_time: Mapped[str | None] = mapped_column(String(64))
    immutable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dataset: Mapped[Dataset] = relationship(back_populates="versions")


class MarketBar(TimestampMixin, Base):
    __tablename__ = "market_bars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_version_id: Mapped[str] = mapped_column(ForeignKey("dataset_versions.id"), nullable=False)
    timestamp: Mapped[str] = mapped_column(String(64), nullable=False)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    spread: Mapped[float] = mapped_column(Float, default=0, nullable=False)


class MarketTick(TimestampMixin, Base):
    __tablename__ = "market_ticks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_version_id: Mapped[str] = mapped_column(ForeignKey("dataset_versions.id"), nullable=False)
    timestamp: Mapped[str] = mapped_column(String(64), nullable=False)
    bid: Mapped[float] = mapped_column(Float, nullable=False)
    ask: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, default=0, nullable=False)


class EconomicEvent(TimestampMixin, Base):
    __tablename__ = "economic_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    timestamp: Mapped[str] = mapped_column(String(64), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)


class DataQualityReport(TimestampMixin, Base):
    __tablename__ = "data_quality_reports"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    dataset_version_id: Mapped[str] = mapped_column(ForeignKey("dataset_versions.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    checks: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    critical_issue_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class FeatureDefinition(TimestampMixin, Base):
    __tablename__ = "feature_definitions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    feature_type: Mapped[str] = mapped_column(String(64), nullable=False)
    config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class FeatureSet(TimestampMixin, Base):
    __tablename__ = "feature_sets"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    feature_definition_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    preprocessing_config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    artifact_uri: Mapped[str | None] = mapped_column(String(512))


class Strategy(TimestampMixin, Base):
    __tablename__ = "strategies"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    family: Mapped[str] = mapped_column(String(64), nullable=False)
    versions: Mapped[list["StrategyVersion"]] = relationship(back_populates="strategy")


class StrategyVersion(TimestampMixin, Base):
    __tablename__ = "strategy_versions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    strategy_id: Mapped[str] = mapped_column(ForeignKey("strategies.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    lifecycle_status: Mapped[str] = mapped_column(String(32), default="DRAFT", nullable=False)
    parameters: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    entry_rules: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    exit_rules: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    immutable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    strategy: Mapped[Strategy] = relationship(back_populates="versions")


class Model(TimestampMixin, Base):
    __tablename__ = "models"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_type: Mapped[str] = mapped_column(String(64), nullable=False)


class ModelVersion(TimestampMixin, Base):
    __tablename__ = "model_versions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    model_id: Mapped[str] = mapped_column(ForeignKey("models.id"), nullable=False)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="DRAFT", nullable=False)
    feature_set_id: Mapped[str | None] = mapped_column(ForeignKey("feature_sets.id"))
    label_definition: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    train_range: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    validation_range: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    test_range: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    artifact_uri: Mapped[str | None] = mapped_column(String(512))
    scaler_artifact_uri: Mapped[str | None] = mapped_column(String(512))
    leakage_check: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class TrainingRun(TimestampMixin, Base):
    __tablename__ = "training_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    model_version_id: Mapped[str] = mapped_column(ForeignKey("model_versions.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class RLTrainingRun(TimestampMixin, Base):
    __tablename__ = "rl_training_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    model_version_id: Mapped[str] = mapped_column(ForeignKey("model_versions.id"), nullable=False)
    observation_schema: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    action_schema: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    reward_config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)


class CostModel(TimestampMixin, Base):
    __tablename__ = "cost_models"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class BacktestConfig(TimestampMixin, Base):
    __tablename__ = "backtest_configs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    strategy_version_id: Mapped[str] = mapped_column(ForeignKey("strategy_versions.id"), nullable=False)
    dataset_version_id: Mapped[str] = mapped_column(ForeignKey("dataset_versions.id"), nullable=False)
    cost_model_id: Mapped[str] = mapped_column(ForeignKey("cost_models.id"), nullable=False)
    config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class BacktestRun(TimestampMixin, Base):
    __tablename__ = "backtest_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    backtest_config_id: Mapped[str] = mapped_column(ForeignKey("backtest_configs.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class BacktestTrade(TimestampMixin, Base):
    __tablename__ = "backtest_trades"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    backtest_run_id: Mapped[str] = mapped_column(ForeignKey("backtest_runs.id"), nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    side: Mapped[str] = mapped_column(String(8), nullable=False)
    entry_time: Mapped[str] = mapped_column(String(64), nullable=False)
    exit_time: Mapped[str | None] = mapped_column(String(64))
    pnl: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    costs: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class PerformanceMetrics(TimestampMixin, Base):
    __tablename__ = "performance_metrics"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    backtest_run_id: Mapped[str] = mapped_column(ForeignKey("backtest_runs.id"), nullable=False)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class WalkForwardFold(TimestampMixin, Base):
    __tablename__ = "walk_forward_folds"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    backtest_run_id: Mapped[str] = mapped_column(ForeignKey("backtest_runs.id"), nullable=False)
    fold_index: Mapped[int] = mapped_column(Integer, nullable=False)
    train_range: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    validation_range: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    test_range: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    selected_parameters: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class OptimizationRun(TimestampMixin, Base):
    __tablename__ = "optimization_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    strategy_version_id: Mapped[str] = mapped_column(ForeignKey("strategy_versions.id"), nullable=False)
    objective: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    result: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class MonteCarloRun(TimestampMixin, Base):
    __tablename__ = "monte_carlo_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    backtest_run_id: Mapped[str] = mapped_column(ForeignKey("backtest_runs.id"), nullable=False)
    result: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class StressTestRun(TimestampMixin, Base):
    __tablename__ = "stress_test_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    backtest_run_id: Mapped[str] = mapped_column(ForeignKey("backtest_runs.id"), nullable=False)
    scenario: Mapped[str] = mapped_column(String(128), nullable=False)
    result: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class RiskProfile(TimestampMixin, Base):
    __tablename__ = "risk_profiles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    limits: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    non_overridable: Mapped[list] = mapped_column(JSON, default=list, nullable=False)


class BrokerAccount(TimestampMixin, Base):
    __tablename__ = "broker_accounts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    broker: Mapped[str] = mapped_column(String(128), nullable=False)
    server: Mapped[str] = mapped_column(String(128), nullable=False)
    account_type: Mapped[str] = mapped_column(String(32), nullable=False)
    masked_account: Mapped[str] = mapped_column(String(32), nullable=False)


class SymbolSpecification(TimestampMixin, Base):
    __tablename__ = "symbol_specifications"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    broker_account_id: Mapped[str] = mapped_column(ForeignKey("broker_accounts.id"), nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    contract_size: Mapped[float] = mapped_column(Float, nullable=False)
    min_lot: Mapped[float] = mapped_column(Float, nullable=False)
    max_lot: Mapped[float] = mapped_column(Float, nullable=False)
    lot_step: Mapped[float] = mapped_column(Float, nullable=False)


class StrategyDeployment(TimestampMixin, Base):
    __tablename__ = "strategy_deployments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    strategy_version_id: Mapped[str] = mapped_column(ForeignKey("strategy_versions.id"), nullable=False)
    model_version_id: Mapped[str | None] = mapped_column(ForeignKey("model_versions.id"))
    broker_account_id: Mapped[str] = mapped_column(ForeignKey("broker_accounts.id"), nullable=False)
    mode: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)


class AutoTradeSession(TimestampMixin, Base):
    __tablename__ = "auto_trade_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    deployment_id: Mapped[str] = mapped_column(ForeignKey("strategy_deployments.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    stop_mode: Mapped[str | None] = mapped_column(String(64))
    state: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class Signal(TimestampMixin, Base):
    __tablename__ = "signals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    deployment_id: Mapped[str] = mapped_column(ForeignKey("strategy_deployments.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(16), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)


class RiskDecision(TimestampMixin, Base):
    __tablename__ = "risk_decisions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    signal_id: Mapped[str] = mapped_column(ForeignKey("signals.id"), nullable=False)
    decision: Mapped[str] = mapped_column(String(16), nullable=False)
    original_volume: Mapped[float] = mapped_column(Float, nullable=False)
    approved_volume: Mapped[float] = mapped_column(Float, nullable=False)
    checks: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    rejection_code: Mapped[str | None] = mapped_column(String(64))


class LiveOrder(TimestampMixin, Base):
    __tablename__ = "live_orders"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    signal_id: Mapped[str] = mapped_column(ForeignKey("signals.id"), nullable=False)
    broker_order_id: Mapped[str | None] = mapped_column(String(128))
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    side: Mapped[str] = mapped_column(String(8), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    broker_response: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class Position(TimestampMixin, Base):
    __tablename__ = "positions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    broker_position_id: Mapped[str | None] = mapped_column(String(128))
    auto_trade_session_id: Mapped[str | None] = mapped_column(ForeignKey("auto_trade_sessions.id"))
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    side: Mapped[str] = mapped_column(String(8), nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)
    open_price: Mapped[float] = mapped_column(Float, nullable=False)
    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)


class RiskEvent(TimestampMixin, Base):
    __tablename__ = "risk_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    auto_trade_session_id: Mapped[str | None] = mapped_column(ForeignKey("auto_trade_sessions.id"))
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    action_taken: Mapped[str] = mapped_column(String(255), nullable=False)


class TradingJournal(TimestampMixin, Base):
    __tablename__ = "trading_journal"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    trade_source: Mapped[str] = mapped_column(String(32), nullable=False)
    trade_id: Mapped[str] = mapped_column(String(64), nullable=False)
    snapshots: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class Alert(TimestampMixin, Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)


class AuditLog(TimestampMixin, Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    actor: Mapped[str] = mapped_column(String(128), nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    before_state: Mapped[dict | None] = mapped_column(JSON)
    after_state: Mapped[dict | None] = mapped_column(JSON)
    correlation_id: Mapped[str] = mapped_column(String(64), nullable=False)
