"""
FloweringAgents — Score calculation engine
"""
import math
from .models import TRANSPARENCY_MULTIPLIER, ORIGIN_MULTIPLIER

def calc_genesis_score(
    ai_involvement_pct: float,
    humans_at_launch: int,
    days_to_revenue: int,
    months_active: int,
    transparency_upgrades: int = 0,
) -> float:
    ai = ai_involvement_pct / 100
    if ai >= 0.80:   op = 1.00
    elif ai >= 0.60: op = 0.75
    elif ai >= 0.40: op = 0.45
    elif ai >= 0.20: op = 0.20
    else:            op = 0.10

    if days_to_revenue <= 30:    bv = 1.00
    elif days_to_revenue <= 90:  bv = 0.75
    elif days_to_revenue <= 180: bv = 0.50
    elif days_to_revenue <= 365: bv = 0.25
    else:                        bv = 0.10

    h = humans_at_launch
    if h <= 1:    har = 1.00
    elif h <= 3:  har = 0.80
    elif h <= 8:  har = 0.55
    elif h <= 20: har = 0.30
    else:         har = 0.05

    lg = min(0.50, (months_active * 0.008) + (transparency_upgrades * 0.020))

    genesis_score = (op * 0.40) + (bv * 0.25) + (har * 0.20) + (lg * 0.15)
    genesis_mult  = min(1.00, 0.10 + genesis_score * 0.90)
    return round(genesis_mult, 4)

def calc_transparency_mult(transparency_level: int) -> float:
    return TRANSPARENCY_MULTIPLIER.get(transparency_level, 0.15)

def calc_econ_base(
    net_pnl: float,
    revenue_growth: float,
    gross_revenue: float,
    total_costs: float,
    human_oversight_pct: float,
) -> float:
    pnl_norm = math.log1p(max(0, net_pnl)) * 1000 if net_pnl > 0 else 0
    growth_score = min(100, max(0, revenue_growth)) * 10
    if total_costs > 0:
        infra_eff = min(5.0, gross_revenue / total_costs) * 2000
    else:
        infra_eff = 0
    autonomy_bonus = (1 - human_oversight_pct / 100) * 2000
    econ_base = (
        pnl_norm      * 0.60 +
        growth_score  * 0.20 +
        infra_eff     * 0.10 +
        autonomy_bonus * 0.10
    )
    return round(econ_base, 2)

def calc_final_score(econ_base, transparency_mult, genesis_mult) -> float:
    return round(econ_base * transparency_mult * genesis_mult, 2)
