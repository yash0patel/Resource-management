from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import pandas as pd


@dataclass(frozen=True)
class StockPlan:
    avg_daily_demand: float
    safety_stock: float
    reorder_point: float
    lead_time: int
    buffer_days: int
    days_until_stockout: Optional[int]
    risk_level: str  # Green/Orange/Red mapped
    recommended_reorder_qty: int


def compute_stock_plan(
    forecast_df: pd.DataFrame,
    *,
    current_stock: float,
    lead_time: int,
    buffer_days: int,
    days_until_stockout: Optional[int],
) -> StockPlan:
    avg_daily_demand = float(forecast_df["Demand"].mean()) if not forecast_df.empty else 0.0
    safety_stock = avg_daily_demand * float(buffer_days)
    reorder_point = avg_daily_demand * float(lead_time) + safety_stock

    # Basic reorder recommendation: cover the reorder point shortfall.
    shortfall = float(reorder_point - float(current_stock))
    recommended_reorder_qty = max(int(round(shortfall)), 0)

    if days_until_stockout is None:
        risk_level = "🟢 Safe"
    else:
        # Risk banding tied to lead time and buffer.
        if days_until_stockout <= lead_time:
            risk_level = "🔴 Critical"
        elif days_until_stockout <= lead_time + buffer_days:
            risk_level = "🟠 Moderate"
        else:
            risk_level = "🟢 Safe"

    return StockPlan(
        avg_daily_demand=avg_daily_demand,
        safety_stock=safety_stock,
        reorder_point=reorder_point,
        lead_time=int(lead_time),
        buffer_days=int(buffer_days),
        days_until_stockout=days_until_stockout,
        risk_level=risk_level,
        recommended_reorder_qty=recommended_reorder_qty,
    )


def build_stock_recommendation_text(plan: StockPlan, *, promotion_enabled: bool) -> list[str]:
    messages: list[str] = []

    if plan.days_until_stockout is None:
        messages.append(
            f"Projected to stay in stock for the full planning horizon (no stockout expected)."
        )
    else:
        if plan.days_until_stockout <= plan.lead_time:
            messages.append(f"Stock will run out in {plan.days_until_stockout} day(s). Reorder immediately to cover lead time.")
        else:
            messages.append(f"Stockout projected in {plan.days_until_stockout} day(s). Reorder within the next {max(plan.lead_time, 1)} day(s).")

    messages.append(f"Maintain a safety buffer of ~{int(round(plan.safety_stock)):,} units.")
    if plan.recommended_reorder_qty > 0:
        messages.append(f"Recommended reorder quantity: {plan.recommended_reorder_qty:,} units (to bring stock back toward the reorder point).")
    else:
        messages.append("Reorder quantity recommendation is 0 units (stock is at/above reorder point).")

    if promotion_enabled:
        messages.append("Promotion flag is enabled for the planning horizon, increasing the model’s Holiday/Promotion feature and expected demand.")

    return messages

