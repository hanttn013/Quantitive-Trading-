# AurumQuant Gap Analysis

**Date:** 2026-06-17  
**Primary source of truth:** `docs/Spec.md`  
**Current implementation reviewed:** FastAPI prototype in `backend/`, frontend wiring in `quant-command/`, previous plan in `docs/plans/2026-06-17-aurumquant-spec-implementation.md`.

---

## Summary

The current implementation is useful as a UI/API integration prototype, but it is not a Spec-compliant quantitative trading platform. It exposes deterministic JSON, safe simulated actions, and a DeepSeek fallback proxy, but it does not yet implement persistence, quantitative domain entities, realistic backtesting, validation, deployment gates, paper trading, broker adapters, or AutoTradeSession runtime.

The corrected plan keeps the current prototype as a temporary shell and refactors it phase by phase into the architecture required by the Spec.

---

## Current Prototype Inventory

| Area | Current State | Status |
| --- | --- | --- |
| FastAPI app and health | Exists | PARTIAL |
| `.venv` dependencies | Exists for FastAPI/Pydantic/pytest | PARTIAL |
| UI read APIs | Return deterministic data | SIMULATED |
| Frontend API client | Exists | PARTIAL |
| Frontend page wiring | Many pages call API with fallback mock data | PARTIAL |
| Copilot | Backend fallback/proxy shape exists, no real provider call | SIMULATED |
| Trading actions | Safe simulation only | SIMULATED |
| Emergency Stop | Safe simulated response only | SIMULATED |
| Tests | Endpoint/status and simple safety tests | PARTIAL |

---

## Spec Gaps

| Required Capability | Current Gap | Required Direction |
| --- | --- | --- |
| SQLAlchemy/Alembic persistence | Not present | Add DB models, migrations, repositories, DI |
| Dataset and DatasetVersion | Not present | Implement persisted dataset lifecycle and immutability |
| MarketBar/MarketTick | Not present | Persist deterministic fixture data and later imports |
| Data quality reports | Not present | Implement validation engine and reports |
| Feature engine | Not present | Add indicators/features with chronology guarantees |
| Strategy/StrategyVersion | Not present | Add lifecycle, versioning, immutable deployed versions |
| Model/ModelVersion/TrainingRun | Not present | Add model registry and training metadata |
| Backtest engine | Mock summary only | Implement actual simulation over market data |
| Cost model | Not real | Implement spread, commission, slippage, swap |
| Backtest trades/metrics | Not generated | Persist trades and calculate metrics |
| Walk-forward validation | Not present | Add fold generation, fit/train/select/evaluate flow |
| Leakage checks | Not present | Add automatic invalidation rules |
| Optimization/robustness | Not present | Add parameter stability, sensitivity, Monte Carlo, stress |
| Deployment gate | Not present | Add explainable gate failures |
| Paper trading | Not present | Add backend session and simulated broker flow |
| AutoTradeSession | Not present | Add backend runtime independent of browser |
| Broker adapter | Not present | Add protocol, simulated adapter, MT5 boundary disabled by default |
| Risk engine | Simplified function only | Add independent engine and persisted RiskDecision/RiskEvent |
| Trading journal | Not present | Persist journal entries |
| Frontend page states | Mostly not present | Add loading/empty/error/degraded/permission-denied states |

---

## Rules Going Forward

1. Do not mark a phase `VERIFIED` unless tests prove Spec acceptance criteria.
2. Do not treat seeded demo data as backtest results.
3. Do not call a Strategy an Agent and skip StrategyVersion/Signal/RiskDecision.
4. Do not expose broker credentials or `DEEPSEEK_API_KEY`.
5. Do not allow live broker execution in tests.
6. Do not optimize or validate using shuffled time-series data.
7. Do not bypass the Risk Engine for Copilot, frontend, broker, strategy, or model actions.

---

## Replacement Decision

The previous plan is replaced. Its completed tasks are reclassified as prototype support only:

```text
FastAPI shell: PARTIAL
Mock read APIs: SIMULATED
Safe trading actions: SIMULATED
Copilot fallback: SIMULATED
Frontend API wiring: PARTIAL
Real quantitative platform: NOT_IMPLEMENTED
```
