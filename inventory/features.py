from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict

from utils.seasonality import season_from_month


@dataclass(frozen=True)
class ForecastContext:
    category: str
    region: str
    weather_condition: str  # Sunny, Rainy, Cloudy, Snowy
    holiday_promotion_flag: int  # 0/1 used by ML feature "Holiday/Promotion"
    inventory_level: float  # used by ML feature "Inventory Level Cleaned"


def one_hot_feature(value: str, prefix: str, options: list[str]) -> Dict[str, int]:
    """
    Create a one-hot mapping like:
      prefix="Category", value="Electronics"
      -> {"Category_Electronics": 1, ...}
    """
    result = {f"{prefix}_{opt}": 0 for opt in options}
    if value not in options:
        return result
    result[f"{prefix}_{value}"] = 1
    return result


def build_model_feature_vector(
    d: date,
    ctx: ForecastContext,
) -> Dict[str, float]:
    """
    Build the model-ready (pre-reindexed) feature dictionary.
    """
    month = int(d.month)
    day = int(d.day)
    year = int(d.year)

    seasonality = season_from_month(d.month)

    features: Dict[str, float] = {
        "Month": float(month),
        "Holiday/Promotion": float(ctx.holiday_promotion_flag),
        "Inventory Level Cleaned": float(ctx.inventory_level),
        "Year": float(year),
        "Day": float(day),
    }

    features.update(
        one_hot_feature(ctx.category, "Category", ["Clothing", "Electronics", "Furniture", "Groceries", "Toys"])
    )
    features.update(
        one_hot_feature(ctx.region, "Region", ["East", "North", "South", "West"])
    )
    features.update(
        one_hot_feature(
            ctx.weather_condition,
            "Weather Condition",
            ["Cloudy", "Rainy", "Snowy", "Sunny"],
        )
    )
    features.update(
        one_hot_feature(seasonality, "Seasonality", ["Autumn", "Spring", "Summer", "Winter"])
    )

    return features

