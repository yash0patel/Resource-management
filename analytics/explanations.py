from __future__ import annotations

import math
from datetime import date
from typing import Callable, Dict, Optional, Tuple

import pandas as pd

from inventory.features import ForecastContext, build_model_feature_vector


def _predict_single(model, d: date, ctx: ForecastContext) -> int:
    input_dict = build_model_feature_vector(d, ctx)
    input_df = pd.DataFrame([input_dict])

    model_columns = getattr(model, "feature_names_in_", None)
    if model_columns is not None:
        input_df = input_df.reindex(columns=model_columns, fill_value=0)

    pred = float(model.predict(input_df)[0])
    return max(int(math.ceil(pred)), 0)


def demand_explanation_for_peak_day(
    model,
    peak_day: date,
    *,
    category: str,
    region: str,
    base_weather_condition: str,
    base_holiday_promotion_flag: int,
    inventory_level: float,
    holiday_info_for_date: Callable[[date], Tuple[int, int, Optional[str]]],
) -> dict:
    """
    Counterfactual explanations for a single high-demand day:
    - Holiday impact (toggle Holiday/Promotion)
    - Weather impact (force Sunny)
    - Seasonal trend (compare across 4 seasons)
    """
    holiday_flag, holiday_promo_flag, _name = holiday_info_for_date(peak_day)
    base_flag = int(base_holiday_promotion_flag)

    baseline_ctx = ForecastContext(
        category=category,
        region=region,
        weather_condition=base_weather_condition,
        holiday_promotion_flag=base_flag,
        inventory_level=inventory_level,
    )

    baseline_demand = _predict_single(model, peak_day, baseline_ctx)

    # Holiday impact: force Holiday/Promotion to 0.
    holiday_off_ctx = ForecastContext(
        category=category,
        region=region,
        weather_condition=base_weather_condition,
        holiday_promotion_flag=0,
        inventory_level=inventory_level,
    )
    demand_without_holiday = _predict_single(model, peak_day, holiday_off_ctx)

    # Weather impact: force Sunny.
    sunny_ctx = ForecastContext(
        category=category,
        region=region,
        weather_condition="Sunny",
        holiday_promotion_flag=base_flag,
        inventory_level=inventory_level,
    )
    demand_weather_sunny = _predict_single(model, peak_day, sunny_ctx)

    # Seasonal trend: test each season one-hot.
    season_names = ["Autumn", "Spring", "Summer", "Winter"]
    season_demands: Dict[str, int] = {}
    for season in season_names:
        # Patch seasonality by swapping month->season one-hot via a dummy ForecastContext:
        # easiest approach: we directly build the feature vector, overriding the seasonality.
        # We'll do this by building a ctx and then adjusting the feature dict.
        ctx = ForecastContext(
            category=category,
            region=region,
            weather_condition=base_weather_condition,
            holiday_promotion_flag=base_flag,
            inventory_level=inventory_level,
        )
        feat = build_model_feature_vector(peak_day, ctx)
        for s in season_names:
            feat[f"Seasonality_{s}"] = 1 if s == season else 0
        input_df = pd.DataFrame([feat])
        model_columns = getattr(model, "feature_names_in_", None)
        if model_columns is not None:
            input_df = input_df.reindex(columns=model_columns, fill_value=0)
        pred = float(model.predict(input_df)[0])
        season_demands[season] = max(int(math.ceil(pred)), 0)

    best_season = max(season_demands.items(), key=lambda kv: kv[1])[0]

    avg_season_demand = sum(season_demands.values()) / max(len(season_demands), 1)
    seasonal_delta = baseline_demand - avg_season_demand

    return {
        "peak_day": peak_day.isoformat(),
        "baseline_demand": baseline_demand,
        "holiday_impact": {
            "baseline": baseline_demand,
            "without_holiday": demand_without_holiday,
            "delta": baseline_demand - demand_without_holiday,
        },
        "weather_impact": {
            "baseline": baseline_demand,
            "weather_as_sunny": demand_weather_sunny,
            "delta": baseline_demand - demand_weather_sunny,
        },
        "seasonality_trend": {
            "best_season": best_season,
            "season_demands": season_demands,
            "seasonal_delta_vs_avg": seasonal_delta,
        },
    }

