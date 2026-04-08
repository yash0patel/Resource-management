from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from typing import Callable, Optional, Tuple

import pandas as pd

from inventory.features import ForecastContext, build_model_feature_vector


@dataclass(frozen=True)
class ForecastRow:
    d: date
    demand: int
    opening_stock: float
    closing_stock: float
    stock_status: str
    weather_condition: str
    holiday_flag: int
    holiday_promotion_flag: int


def _predict_demand_for_day(
    model,
    d: date,
    ctx: ForecastContext,
) -> int:
    input_dict = build_model_feature_vector(d, ctx)
    input_df = pd.DataFrame([input_dict])

    model_columns = getattr(model, "feature_names_in_", None)
    if model_columns is not None:
        input_df = input_df.reindex(columns=model_columns, fill_value=0)

    pred = float(model.predict(input_df)[0])
    return max(int(math.ceil(pred)), 0)


def forecast_inventory(
    model,
    start_date: date,
    end_date: date,
    *,
    inventory_level: float,
    category: str,
    region: str,
    apply_promotion: bool,
    weather_condition_for_date: Callable[[date], str],
    holiday_info_for_date: Callable[[date], Tuple[int, int, Optional[str]]],
    weather_override: Optional[str] = None,
    demand_multiplier: float = 1.0,
    holiday_promotion_override: Optional[int] = None,  # 0/1 constant override for Holiday/Promotion
) -> Tuple[pd.DataFrame, dict]:
    """
    Run a date-wise inventory forecast:
    - Use the ML model to predict daily demand/consumption.
    - Deplete stock using predicted demand.

    Returns: (forecast_df, meta)
    """
    if end_date < start_date:
        raise ValueError("end_date must be >= start_date")

    date_range = pd.date_range(start=start_date, end=end_date, freq="D")

    rows: list[dict] = []
    current_stock_balance = float(inventory_level)

    for target_day in date_range:
        d = target_day.date()

        weather_condition = weather_override or weather_condition_for_date(d)
        holiday_flag, _holiday_promo_flag, holiday_name = holiday_info_for_date(d)
        # Apply promotion toggle overrides holiday for the ML feature "Holiday/Promotion".
        holiday_promo_flag = int(1 if apply_promotion else holiday_flag)

        if holiday_promotion_override is not None:
            holiday_promo_flag = int(holiday_promotion_override)

        ctx = ForecastContext(
            category=category,
            region=region,
            weather_condition=weather_condition,
            holiday_promotion_flag=holiday_promo_flag,
            inventory_level=inventory_level,  # keep behavior aligned with existing app
        )

        demand = _predict_demand_for_day(model, d, ctx)
        demand = int(max(round(demand * float(demand_multiplier)), 0))

        opening_stock = current_stock_balance
        closing_stock = opening_stock - demand
        current_stock_balance = closing_stock

        stock_status = "Available" if closing_stock >= 0 else "Shortage"

        rows.append(
            {
                "Date": d,
                "Weather Condition": weather_condition,
                "Holiday": int(holiday_flag),
                "Holiday Name": holiday_name,
                "Holiday/Promotion": int(holiday_promo_flag),
                "Demand": demand,
                "Opening Stock": opening_stock,
                "Closing Stock": closing_stock,
                "Stock Status": stock_status,
            }
        )

    df = pd.DataFrame(rows)
    df["Total Demand Till Date"] = df["Demand"].cumsum()

    # Stockout analysis
    stockout_mask = df["Closing Stock"] < 0
    if stockout_mask.any():
        stockout_idx = int(stockout_mask.idxmax())
        stockout_date = df.loc[stockout_idx, "Date"]
        days_until_stockout = stockout_idx
    else:
        stockout_date = None
        days_until_stockout = None

    meta = {
        "stockout_date": stockout_date,
        "days_until_stockout": days_until_stockout,
    }
    return df, meta

