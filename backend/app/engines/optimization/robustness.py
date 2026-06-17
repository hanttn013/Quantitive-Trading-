from __future__ import annotations

import random


def monte_carlo_sequence(pnls: list[float], *, runs: int = 100, seed: int = 616, ruin_level: float = -500.0) -> dict[str, float]:
    rng = random.Random(seed)
    ruins = 0
    worst = 0.0
    for _ in range(runs):
        shuffled = pnls[:]
        rng.shuffle(shuffled)
        cumulative = 0.0
        path_worst = 0.0
        for pnl in shuffled:
            cumulative += pnl
            path_worst = min(path_worst, cumulative)
        worst = min(worst, path_worst)
        if path_worst <= ruin_level:
            ruins += 1
    return {"runs": float(runs), "probability_of_ruin": ruins / runs if runs else 0.0, "worst_path_pnl": worst}


def stress_costs(metrics: dict[str, float], *, spread_multiplier: float = 2.0, slippage_multiplier: float = 2.0) -> dict[str, float]:
    spread = metrics.get("spread_cost", 0.0) * (spread_multiplier - 1)
    slippage = metrics.get("slippage_cost", 0.0) * (slippage_multiplier - 1)
    stressed_net = metrics.get("net_profit", 0.0) - spread - slippage
    return {"stressed_net_profit": stressed_net, "extra_spread_cost": spread, "extra_slippage_cost": slippage}
