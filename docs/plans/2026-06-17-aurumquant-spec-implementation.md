# AurumQuant Corrected Spec Implementation Plan

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Replace the prototype-only implementation path with a Spec-compliant platform plan that incrementally converts the existing FastAPI/UI prototype into a persisted quantitative research, validation, backtesting, risk, paper trading, and execution-safety platform.

**Architecture:** Preserve the existing `quant-command` UI and the FastAPI prototype as a temporary integration shell, but move backend runtime state into SQLAlchemy repositories, domain services, quantitative engines, and broker adapters. Seeded demo data is allowed only through database seeds/repositories; mock dictionaries may remain only as migration aids and tests fixtures until removed.

**Tech Stack:** Python `.venv`, FastAPI, Pydantic, SQLAlchemy 2.x, Alembic, SQLite local database with PostgreSQL-compatible models, pytest, React, Vite, TypeScript, TanStack Query.

**Current implementation status:** `PROTOTYPE / SIMULATED / PARTIAL`. It is not Spec-complete and must not be represented as a completed trading platform.

---

## Status Taxonomy

Use these labels in `docs/plans/task.md`, API metadata, and phase reports:

```text
NOT_IMPLEMENTED - no meaningful implementation exists.
PARTIAL - some structure exists, but acceptance criteria are incomplete.
SIMULATED - deterministic development behavior exists; not production behavior.
IMPLEMENTED - feature exists and is wired, but final verification may be incomplete.
VERIFIED - feature has tests proving the Spec acceptance criteria.
```

---

## Phase 0: Repository Audit And Corrected Plan

**Purpose:** Stop treating mock/API wiring as Spec completion and create the correct implementation baseline.

**Files:**
- Create: `docs/plans/2026-06-17-aurumquant-gap-analysis.md`
- Replace: `docs/plans/2026-06-17-aurumquant-spec-implementation.md`
- Replace: `docs/plans/task.md`

**Steps:**
1. Read `docs/Spec.md`.
2. Audit backend, frontend, and current plan.
3. Compare current prototype to required Spec domains.
4. Document gaps using the status taxonomy.
5. Replace the plan with this corrected phase plan.
6. Reset tracker so completed prototype work is marked as `SIMULATED` or `PARTIAL`, not complete.

**Verification:**
- `docs/plans/2026-06-17-aurumquant-gap-analysis.md` exists.
- `docs/plans/task.md` contains phase-level statuses.
- No phase that depends on persistence, real backtesting, validation, deployment gate, paper trading, or execution is marked complete.

---

## Phase 1: Backend Foundation With Persistence

**Purpose:** Add the real backend foundation required by the Spec without breaking the existing UI.

**Files:**
- Modify: `backend/requirements.txt`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/versions/`
- Create: `backend/app/db/base.py`
- Create: `backend/app/db/session.py`
- Create: `backend/app/db/models.py`
- Create: `backend/app/dependencies.py`
- Create: `backend/app/errors.py`
- Modify: `backend/app/settings.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_database_foundation.py`

**Steps:**
1. Add SQLAlchemy 2.x and Alembic to `.venv` requirements.
2. Define database settings for SQLite local development.
3. Create SQLAlchemy base, engine, session factory, and FastAPI dependencies.
4. Add Alembic configuration.
5. Add structured API error responses.
6. Preserve current health route.
7. Add tests proving tables can be created and sessions work.

**Acceptance Criteria:**
- Database tables can be created in a temporary SQLite database.
- FastAPI routes can receive a database session via dependency injection.
- No endpoint exposes secrets.

---

## Phase 2: Core Domain Models And Repositories

**Purpose:** Implement real persisted entities from `docs/Spec.md`.

**Files:**
- Create/modify SQLAlchemy models in `backend/app/db/models.py`
- Create: `backend/app/repositories/`
- Create: `backend/app/schemas/`
- Create: `backend/app/seeds/demo.py`
- Create tests under `backend/tests/domain/`

**Required entities:**
- Data: `Dataset`, `DatasetVersion`, `MarketBar`, `MarketTick`, `EconomicEvent`, `DataQualityReport`
- Features: `FeatureDefinition`, `FeatureSet`, preprocessing config/artifact metadata
- Strategy: `Strategy`, `StrategyVersion`, strategy params, entry/exit rules, lifecycle status
- Model: `Model`, `ModelVersion`, `TrainingRun`, `RLTrainingRun`, artifact/scaler refs, leakage results
- Backtest: `BacktestConfig`, `BacktestRun`, `BacktestTrade`, `PerformanceMetrics`, `WalkForwardFold`, `CostModel`, `OptimizationRun`, `MonteCarloRun`, `StressTestRun`
- Risk/trading: `RiskProfile`, `StrategyDeployment`, `AutoTradeSession`, `Signal`, `RiskDecision`, `LiveOrder`, `Position`, `RiskEvent`, `TradingJournal`, `Alert`, `AuditLog`, `BrokerAccount`, `SymbolSpecification`

**Steps:**
1. Implement models with relationships and timestamps.
2. Add repository classes by domain.
3. Seed demo entities through repositories.
4. Keep UI compatibility routes, but source them from repositories.
5. Mark any UI-only `Agent` as a projection of deployment/model state, not a replacement for Strategy/Model/Signal.

**Acceptance Criteria:**
- Repositories persist and retrieve records from SQLite.
- StrategyVersion can be immutable after deployment/use.
- Demo data is stored in the database, not served only from `mock_data.py`.

---

## Phase 3: Market Data And Data Center

**Purpose:** Add dataset ingestion, versioning, validation, and market data access.

**Files:**
- Create: `backend/app/engines/data/`
- Create: `backend/app/routes/data.py`
- Create tests under `backend/tests/data/`
- Add frontend hooks/pages only where needed.

**Steps:**
1. Implement dataset creation and dataset version creation.
2. Implement OHLC bar ingestion from deterministic fixtures.
3. Implement data validation: missing candles, duplicates, timestamp ordering, high/low consistency, negative spread, invalid volume, timezone metadata.
4. Store `DataQualityReport`.
5. Add economic events and news blackout data.
6. Add API groups for datasets, versions, reports, bars, ticks, economic calendar, market watch, feed integrity.

**Acceptance Criteria:**
- DatasetVersion is immutable once used by a run.
- Data quality report can block invalid live validation.
- Tests cover missing bars, duplicates, and invalid OHLC.

---

## Phase 4: Feature And Strategy Engine

**Purpose:** Create shared strategy interface for backtest, paper, and live parity.

**Files:**
- Create: `backend/app/engines/features/`
- Create: `backend/app/engines/strategies/`
- Create tests under `backend/tests/strategies/`

**Steps:**
1. Implement feature definitions and feature set references.
2. Implement indicator calculations: Bollinger Bands, RSI, ATR, EMA20/EMA50, z-score, body ratio, wick ratio, session, spread.
3. Implement shared strategy signal contract.
4. Implement `XAU/USD M5 Mean Reversion` with buy/sell/no-trade paths.
5. Implement HMM regime detection contract and strategy switching boundary.
6. Implement ML Liquidity Sweep classifier label/feature contracts.

**Acceptance Criteria:**
- Mean Reversion produces deterministic signals from fixture bars.
- Uncertain HMM regime returns `NO_TRADE`.
- Strategy code is shared by backtest and paper/live evaluation paths.

---

## Phase 5: Realistic Backtest Engine

**Purpose:** Replace hard-coded backtest summary with actual simulation over market data.

**Files:**
- Create: `backend/app/engines/backtest/`
- Modify: backtest routes/repositories
- Create tests under `backend/tests/backtest/`

**Steps:**
1. Implement cost model: fixed/historical spread, commission, slippage, swap.
2. Implement next-bar-open market execution.
3. Implement stop loss, take profit, time-based exits, session/news filters, warm-up bars, closed-candle-only default.
4. Generate `BacktestTrade` rows.
5. Calculate performance metrics from trades and equity curve.
6. Persist `BacktestRun`, trades, metrics, and cost breakdown.

**Acceptance Criteria:**
- Backtest results are not hard-coded.
- Costs reduce gross profit.
- Tests assert known deterministic trade count and PnL from fixture data.

---

## Phase 6: Validation, Optimization, And Robustness

**Purpose:** Implement time-series-safe validation and anti-overfitting tools.

**Files:**
- Create: `backend/app/engines/validation/`
- Create: `backend/app/engines/optimization/`
- Create tests under `backend/tests/validation/`

**Steps:**
1. Implement Train/Validation/Test split.
2. Implement anchored, rolling, and non-anchored walk-forward fold generation.
3. Ensure preprocessing fits only on train range.
4. Implement leakage checks: scaler on test data, negative shifts, future bars, full-series preprocessing, label overlap, shuffle.
5. Implement optimization objective components.
6. Implement parameter stability, spread/slippage/cost sensitivity, Monte Carlo sequence simulation, stress scenarios, probability of ruin.

**Acceptance Criteria:**
- Leakage invalidates runs and excludes them from rankings.
- Optimization never uses final Test Set.
- Walk-forward folds are persisted and non-overlapping according to config.

---

## Phase 7: Model Training And AI Boundaries

**Purpose:** Add model domain behavior without pretending every model is production-ready.

**Files:**
- Create: `backend/app/engines/models/`
- Create tests under `backend/tests/models/`

**Steps:**
1. Implement ML Liquidity Sweep label generation.
2. Implement classifier metrics: precision, recall, F1, confusion matrix, PR-AUC when available, calibration metadata.
3. Mark models with positive prediction metrics but negative expectancy as `PREDICTIVELY_VALID / TRADING_INVALID`.
4. Add HMM model versioning and state-statistics labeling.
5. Create RL environment schema, action schema, observation schema, reward config, and deterministic tests.

**Acceptance Criteria:**
- ModelVersion references feature set, label definition, train/validation/test ranges, artifacts, and leakage results.
- RL action path cannot bypass Risk Engine.

---

## Phase 8: Deployment Gates And Paper Trading

**Purpose:** Enforce Strategy lifecycle and paper trading before live.

**Files:**
- Create: `backend/app/engines/risk/`
- Create: `backend/app/services/deployment.py`
- Create: `backend/app/services/paper_trading.py`
- Create tests under `backend/tests/deployment/`

**Steps:**
1. Implement lifecycle: `DRAFT`, `BACKTESTED`, `VALIDATED`, `PAPER_TRADING`, `PAPER_APPROVED`, `LIVE_APPROVED`, `LIVE`, `PAUSED`, `RETIRED`.
2. Implement Deployment Gate 1-5 with explainable failure reasons.
3. Implement paper trading session using simulated broker.
4. Generate Signals, RiskDecisions, Orders, Positions, and TradingJournal rows.

**Acceptance Criteria:**
- Strategy cannot enter Paper or Live based only on positive Net Profit.
- Gate failures are returned by API.
- Paper trading persists lifecycle entities independent of browser state.

---

## Phase 9: Auto Trade And Execution Safety

**Purpose:** Add backend AutoTradeSession and broker boundary.

**Files:**
- Create: `backend/app/engines/execution/`
- Create: `backend/app/adapters/brokers/`
- Create tests under `backend/tests/execution/`

**Steps:**
1. Define `BrokerAdapter` protocol.
2. Implement `SimulatedBrokerAdapter`.
3. Create MT5 adapter boundary disabled by default behind explicit environment flag.
4. Implement AutoTradeSession statuses.
5. Implement runtime flow: market event -> features -> regime -> strategy -> signal -> risk -> execution -> journal.
6. Implement reconciliation after reconnect/restart.
7. Implement emergency stop and stop modes.

**Acceptance Criteria:**
- Tests use simulated broker only.
- Live MT5 mode disabled by default.
- Unknown order state does not cause blind retries.
- Browser closing does not stop AutoTradeSession.

---

## Phase 10: Frontend API Integration Hardening

**Purpose:** Preserve UI while replacing hard-coded data with feature-specific hooks and states.

**Files:**
- Modify: `quant-command/src/lib/api.ts`
- Add: `quant-command/src/hooks/api/`
- Modify existing pages/components incrementally
- Add frontend tests where practical

**Steps:**
1. Replace generic API calls with typed TanStack Query hooks.
2. Add loading, empty, error, degraded provider, and permission-denied states.
3. Wire Data, Strategy, Backtest, Risk, Deployment, Trading, Alerts, Logs, Integrations, Settings to real domain APIs.
4. Keep visual design and layout intact.

**Acceptance Criteria:**
- Pages do not depend on one giant context response.
- Frontend never receives secrets or broker credentials.
- Build and tests pass.

---

## Phase 11: Copilot Through Normal Safety Path

**Purpose:** Keep Copilot optional and unable to bypass permission/risk/deployment gates.

**Files:**
- Modify: `backend/app/services/copilot.py`
- Modify: `backend/app/routes/copilot.py`
- Add tests under `backend/tests/copilot/`

**Steps:**
1. Keep DeepSeek API key backend-only.
2. Add deterministic fallback.
3. Route Copilot commands through permission checks, deployment state, risk engine, and normal command confirmation flow.
4. Audit simulate/confirm/reject commands.

**Acceptance Criteria:**
- Copilot commands cannot place broker orders directly.
- API key is never returned.
- Command confirmation produces AuditLog correlation ID.

---

## Phase 12: Verification And Documentation

**Purpose:** Prove behavior rather than endpoint existence.

**Files:**
- Modify: `README.md`
- Modify: `.env.example`
- Add verification docs as needed

**Required test coverage:**
- Dataset version immutability.
- No random time-series split/shuffle.
- Scalers fit only on train.
- Future-looking features rejected.
- Backtest costs reduce gross profit.
- SL/TP deterministic execution.
- Walk-forward folds do not overlap incorrectly.
- Optimization does not use final test set.
- Leakage invalidates run.
- Prediction-valid/trading-invalid model cannot pass deployment.
- Risk rejects excess exposure and high spread.
- Daily loss/drawdown stops sessions.
- News blackout blocks entry.
- Emergency Stop creates audit correlation ID.
- AutoTradeSession persists without browser.
- Reconnection performs reconciliation.
- Secrets are never returned.
- Simulated broker used during tests.
- Live MT5 disabled by default.

**Acceptance Criteria:**
- Backend tests pass.
- Frontend tests pass.
- Frontend production build passes.
- Documentation explains venv, DB migrations, seeds, API startup, frontend startup, and DeepSeek/MT5 safety flags.
