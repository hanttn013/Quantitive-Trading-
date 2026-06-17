from app import repository


def test_repository_exposes_spec_core_context():
    context = repository.context()

    assert context.environment == "Paper"
    assert context.account.id == "acc-demo"
    assert {account.type for account in context.accounts} >= {"Demo", "Prop", "Live", "Research"}


def test_repository_exposes_agent_position_and_model_fields():
    agent = repository.agents()[0]
    position = repository.positions()[0]
    model = repository.models()[0]

    assert agent.status in {"Running", "Paused", "Waiting", "Error"}
    assert agent.confidence >= 0
    assert position.symbol == "XAUUSD"
    assert position.risk_pct > 0
    assert model.status == "Live"
    assert model.backtest_sharpe > 0


def test_repository_covers_operational_surfaces():
    assert len(repository.dashboard_metrics()) >= 14
    assert repository.risk_monitor().level == "High Risk"
    assert len(repository.risk_rules()) >= 20
    assert repository.market_watch()[0].symbol == "XAUUSD"
    assert repository.feed_integrity()[-1].status == "warn"
    assert repository.alerts()[0].status == "Open"
    assert repository.audit_logs()[0].correlation_id
    assert {item.id for item in repository.integrations()} >= {"mt5", "discord", "tradingview", "deepseek"}
    assert len(repository.roles()) == 7
    assert repository.backtest_summary().config.symbol == "XAUUSD"
