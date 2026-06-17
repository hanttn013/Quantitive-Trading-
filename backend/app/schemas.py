from typing import Literal

from pydantic import BaseModel, Field


Environment = Literal["Backtest", "Paper", "Live"]


class Account(BaseModel):
    id: str
    label: str
    type: Literal["Demo", "Prop", "Live", "Research"]
    broker: str
    server: str
    masked: str
    balance: float
    equity: float
    free_margin: float
    margin_level: float
    floating_pnl: float
    daily_pnl: float
    latency_ms: int


class AppContext(BaseModel):
    environment: Environment
    account: Account
    accounts: list[Account]


class Metric(BaseModel):
    label: str
    value: str
    delta: float | None = None
    tone: Literal["default", "pos", "neg", "warn"] = "default"
    hint: str | None = None


class Agent(BaseModel):
    id: str
    name: str
    symbol: str
    timeframe: str
    model: str
    status: Literal["Running", "Paused", "Waiting", "Error"]
    action: Literal["Buy", "Sell", "Hold"]
    confidence: float = Field(ge=0, le=1)
    regime: str
    reward: float
    session_reward: float
    trades_today: int
    daily_pnl: float
    drawdown: float
    latency_ms: int
    updated_at: str


class Position(BaseModel):
    ticket: str
    symbol: str
    side: Literal["Buy", "Sell"]
    volume: float
    entry: float
    current: float
    sl: float
    tp: float
    pnl: float
    swap: float
    commission: float
    duration_min: int
    strategy: str
    agent: str
    confidence: float | None
    risk_pct: float
    status: Literal["AI", "Manual", "Managed"]


class RiskMetric(BaseModel):
    label: str
    value: float
    max: float
    warn: float
    critical: float
    unit: str | None = None


class RiskRule(BaseModel):
    name: str
    enabled: bool
    threshold: str
    warning: str
    critical: str
    action: str
    priority: Literal["Low", "Medium", "High", "Critical"]
    non_overridable: bool = False


class RiskMonitor(BaseModel):
    score: int
    level: Literal["Low Risk", "Medium Risk", "High Risk", "Critical"]
    message: str
    metrics: list[RiskMetric]


class AIModel(BaseModel):
    id: str
    name: str
    algorithm: str
    version: str
    trained: str
    status: Literal[
        "Live",
        "Paper Trading",
        "Approved",
        "Training",
        "Validating",
        "Paused",
        "Deprecated",
        "Failed",
        "Draft",
    ]
    steps: int
    validation_score: float
    backtest_sharpe: float
    max_dd: float
    live_sharpe: float | None
    live_dd: float | None
    drift: float
    last_retrain: str


class EquityPoint(BaseModel):
    label: str
    equity: float
    drawdown: float


class PortfolioSummary(BaseModel):
    equity_curve: list[EquityPoint]
    pnl_by_symbol: dict[str, float]
    heatmap: list[float]


class MarketQuote(BaseModel):
    symbol: str
    bid: float
    ask: float
    spread: float
    volatility: str
    tick_rate: str
    latency_ms: int
    feeds: dict[str, Literal["ok", "warn", "error"]]


class FeedIntegrity(BaseModel):
    name: str
    status: Literal["ok", "warn", "error"]
    latency_ms: int
    message: str | None = None


class CalendarEvent(BaseModel):
    title: str
    severity: Literal["Low", "Medium", "High"]
    eta: str
    affected_currency: str


class Alert(BaseModel):
    id: str
    severity: Literal["Critical", "High", "Medium", "Low", "Info"]
    source: str
    account: str
    agent: str
    symbol: str
    time: str
    message: str
    status: Literal["Open", "Ack", "Resolved"]


class AuditEntry(BaseModel):
    timestamp: str
    user: str
    source: str
    account: str
    action: str
    previous: str | None = None
    next: str | None = None
    result: Literal["OK", "REJECTED", "PENDING"]
    correlation_id: str
    latency_ms: int


class Integration(BaseModel):
    id: str
    name: str
    status: Literal["Connected", "Online", "Enabled", "Degraded", "Disconnected"]
    fields: dict[str, str]


class RolePermission(BaseModel):
    role: str
    permissions: dict[str, bool]


class BacktestConfig(BaseModel):
    strategy: str
    model: str
    symbol: str
    timeframe: str
    date_range: str
    capital: str
    spread: str
    commission: str
    swap: str
    slippage: str
    latency: str
    leverage: str
    train: str
    validation: str
    test: str
    walk_forward: str
    monte_carlo: str
    seed: str


class BacktestResult(BaseModel):
    label: str
    value: str
    tone: Literal["default", "pos", "neg", "warn"] = "default"


class BacktestSummary(BaseModel):
    config: BacktestConfig
    equity_curve: list[EquityPoint]
    results: list[BacktestResult]

