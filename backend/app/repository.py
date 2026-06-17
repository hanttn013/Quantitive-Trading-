from __future__ import annotations

from . import mock_data as data
from .schemas import (
    Account,
    Agent,
    AIModel,
    Alert,
    AppContext,
    AuditEntry,
    BacktestConfig,
    BacktestResult,
    BacktestSummary,
    CalendarEvent,
    EquityPoint,
    FeedIntegrity,
    Integration,
    MarketQuote,
    Metric,
    PortfolioSummary,
    Position,
    RiskMetric,
    RiskMonitor,
    RiskRule,
    RolePermission,
)


def accounts() -> list[Account]:
    return [Account(**item) for item in data.ACCOUNTS]


def context(environment: str = "Paper", account_id: str = "acc-demo") -> AppContext:
    all_accounts = accounts()
    selected = next((account for account in all_accounts if account.id == account_id), all_accounts[0])
    return AppContext(environment=environment, account=selected, accounts=all_accounts)


def dashboard_metrics() -> list[Metric]:
    return [
        Metric(label="Balance", value="$10,250.00", delta=0.42),
        Metric(label="Equity", value="$10,184.30", delta=-0.21, tone="neg"),
        Metric(label="Floating PnL", value="-$65.70", delta=-0.64, tone="neg"),
        Metric(label="Day PnL", value="+$184.30", delta=1.83, tone="pos"),
        Metric(label="Week PnL", value="+$612.45", delta=6.10, tone="pos"),
        Metric(label="Month PnL", value="+$2,140.20", delta=21.40, tone="pos"),
        Metric(label="Drawdown", value="1.8%", hint="Max 4.2%", tone="warn"),
        Metric(label="Win Rate", value="61%", hint="42 / 69 trades"),
        Metric(label="Profit Factor", value="1.42", delta=0.08, tone="pos"),
        Metric(label="Sharpe", value="1.71", hint="30d rolling"),
        Metric(label="Sortino", value="2.24", hint="30d rolling"),
        Metric(label="Exposure", value="3.4%", hint="of equity"),
        Metric(label="Margin Usage", value="8.4%", hint="Free $9,810"),
        Metric(label="Realized PnL", value="$2,540.10", tone="pos"),
    ]


def agents() -> list[Agent]:
    return [Agent(**item) for item in data.AGENTS]


def positions() -> list[Position]:
    return [Position(**item) for item in data.POSITIONS]


def risk_monitor() -> RiskMonitor:
    metrics = [RiskMetric(**item) for item in data.RISK_METRICS]
    return RiskMonitor(
        score=72,
        level="High Risk",
        message="Daily loss approaching warn threshold; XAUUSD spread anomaly active.",
        metrics=metrics,
    )


def risk_rules() -> list[RiskRule]:
    rows = [
        ("Max risk per trade", "0.50%", "0.75%", "0.90%", "High"),
        ("Max daily loss", "-$300", "-$250", "-$450", "Critical"),
        ("Max weekly loss", "-$1,200", "-$900", "-$1,500", "Critical"),
        ("Max drawdown", "5%", "4%", "7%", "Critical"),
        ("Max account exposure", "3%", "2.5%", "4%", "High"),
        ("Max symbol exposure", "1.5%", "1.2%", "2%", "High"),
        ("Max correlated exposure", "2.5%", "2%", "3%", "Medium"),
        ("Max positions", "8", "6", "10", "Medium"),
        ("Max trades / day", "40", "30", "50", "Medium"),
        ("Max lot size", "1.0", "0.5", "2.0", "Medium"),
        ("Min margin level", "150%", "200%", "120%", "Critical"),
        ("Max spread", "30 pt", "20 pt", "40 pt", "High"),
        ("Max slippage", "5 pt", "3 pt", "8 pt", "Medium"),
        ("No trading near news", "+/-15m", "-", "-", "High"),
        ("Allowed sessions", "London + NY", "-", "-", "Low"),
        ("Cooldown after loss streak", "3 trades", "2", "5", "Medium"),
        ("Stop on latency anomaly", ">300ms", "200ms", "500ms", "High"),
        ("Stop on MT5 disconnect", "instant", "-", "-", "Critical"),
        ("Stop on feed mismatch", "5pt", "3pt", "8pt", "High"),
        ("Stop on model drift", "0.40", "0.30", "0.50", "High"),
    ]
    return [
        RiskRule(
            name=name,
            enabled=True,
            threshold=threshold,
            warning=warning,
            critical=critical,
            action="Pause + Notify",
            priority=priority,
            non_overridable=priority == "Critical",
        )
        for name, threshold, warning, critical, priority in rows
    ]


def models() -> list[AIModel]:
    return [AIModel(**item) for item in data.MODELS]


def portfolio() -> PortfolioSummary:
    return PortfolioSummary(
        equity_curve=[EquityPoint(**item) for item in data.equity_curve()],
        pnl_by_symbol={"XAUUSD": 1240, "EURUSD": 412, "USDJPY": 188, "BTCUSD": -142, "GBPUSD": 90},
        heatmap=[round((i % 13 - 6) * 12.5, 2) for i in range(112)],
    )


def market_watch() -> list[MarketQuote]:
    rows = [
        ("XAUUSD", 2335.90, 2336.10, 2.0, "High"),
        ("EURUSD", 1.08475, 1.08478, 0.3, "Low"),
        ("BTCUSD", 67882, 67898, 16.0, "Very High"),
        ("USDJPY", 157.40, 157.42, 0.2, "Medium"),
        ("GBPUSD", 1.27210, 1.27214, 0.4, "Low"),
        ("US500", 5421.2, 5421.8, 0.6, "Medium"),
    ]
    return [
        MarketQuote(
            symbol=symbol,
            bid=bid,
            ask=ask,
            spread=spread,
            volatility=volatility,
            tick_rate="12/s",
            latency_ms=38 if symbol == "XAUUSD" else 62,
            feeds={"MT5": "ok", "TV": "ok", "Ext": "warn" if symbol == "XAUUSD" else "ok"},
        )
        for symbol, bid, ask, spread, volatility in rows
    ]


def feed_integrity() -> list[FeedIntegrity]:
    return [
        FeedIntegrity(name="MT5 Broker Feed", status="ok", latency_ms=38),
        FeedIntegrity(name="TradingView Feed", status="ok", latency_ms=62),
        FeedIntegrity(name="External Provider", status="warn", latency_ms=210, message="XAUUSD differs from MT5 by 4.2pt."),
    ]


def calendar() -> list[CalendarEvent]:
    return [
        CalendarEvent(title="USD CPI", severity="High", eta="in 14m", affected_currency="USD"),
        CalendarEvent(title="EUR ECB Speak", severity="Medium", eta="2h 12m", affected_currency="EUR"),
        CalendarEvent(title="GBP Retail Sales", severity="Medium", eta="tomorrow", affected_currency="GBP"),
    ]


def alerts() -> list[Alert]:
    return [Alert(**item) for item in data.ALERTS]


def audit_logs() -> list[AuditEntry]:
    return [AuditEntry(**item) for item in data.AUDIT_LOG]


def integrations() -> list[Integration]:
    return [
        Integration(id="mt5", name="MetaTrader 5", status="Connected", fields={"Broker": "IC Markets", "Server": "ICMarkets-Live18", "Account": ".... 9032", "Heartbeat": "2s", "Ping": "38ms", "Execution": "Enabled"}),
        Integration(id="discord", name="Discord", status="Online", fields={"Server": "QuantAI Ops", "Channel": "#trading-ops", "Synced users": "6", "Allowed cmds": "close, pause, risk, report", "Approval": "Required", "Notifications": "All"}),
        Integration(id="tradingview", name="TradingView", status="Enabled", fields={"Provider": "TradingView Pro", "Symbol map": "12 pairs", "TF map": "All", "Webhooks": "2 active", "Alert sync": "Enabled"}),
        Integration(id="deepseek", name="DeepSeek", status="Degraded", fields={"Provider": "DeepSeek API", "Model": "deepseek-chat", "Secret": "env:DEEPSEEK_API_KEY", "Fallback": "Enabled"}),
    ]


def roles() -> list[RolePermission]:
    permissions = ["View dashboards", "Execute trades", "Approve AI actions", "Pause agents", "Modify risk rules", "Deploy models", "Manage integrations", "Emergency stop", "View audit log"]
    matrix = {
        "Owner": [True, True, True, True, True, True, True, True, True],
        "Admin": [True, True, True, True, True, True, True, True, True],
        "Quant Researcher": [True, False, False, True, False, True, False, False, True],
        "Trader": [True, True, True, True, False, False, False, False, True],
        "Risk Manager": [True, False, True, True, True, False, False, True, True],
        "Viewer": [True, False, False, False, False, False, False, False, True],
        "Discord Operator": [True, False, True, False, False, False, False, False, False],
    }
    return [RolePermission(role=role, permissions=dict(zip(permissions, values, strict=True))) for role, values in matrix.items()]


def backtest_summary() -> BacktestSummary:
    config = BacktestConfig(
        strategy="PPO Gold Scalper",
        model="PPO-v12",
        symbol="XAUUSD",
        timeframe="M5",
        date_range="2024-01 -> 2026-06",
        capital="$10,000",
        spread="2.0 pt",
        commission="$3.5",
        swap="auto",
        slippage="1.0 pt",
        latency="45 ms",
        leverage="1:100",
        train="60%",
        validation="20%",
        test="20%",
        walk_forward="6x3m",
        monte_carlo="1000",
        seed="42",
    )
    results = [
        ("Net Profit", "+$3,184", "pos"),
        ("CAGR", "42.1%", "pos"),
        ("Sharpe", "2.14", "pos"),
        ("Sortino", "2.88", "pos"),
        ("Calmar", "4.92", "pos"),
        ("Max DD", "6.8%", "neg"),
        ("Profit Factor", "1.62", "pos"),
        ("Expectancy", "$3.41", "pos"),
        ("Win Rate", "58%", "default"),
        ("Avg Win", "$14.20", "pos"),
        ("Avg Loss", "-$8.10", "neg"),
        ("Trades", "412", "default"),
        ("Turnover", "21.4x", "default"),
        ("Recovery", "5.8", "pos"),
    ]
    return BacktestSummary(
        config=config,
        equity_curve=[EquityPoint(**item) for item in data.equity_curve()],
        results=[BacktestResult(label=label, value=value, tone=tone) for label, value, tone in results],
    )

