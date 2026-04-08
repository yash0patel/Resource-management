from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib

# Keep the existing model-loading strategy so we do not break runtime ML behavior.
MODEL_CANDIDATES = [
    Path("models/best_resource_model.joblib"),
    Path("best_sales_model.joblib"),
    Path("Sales_model.pkl"),
]

REQUIRED_MODEL_FEATURES = {
    "Month",
    "Holiday/Promotion",
    "Inventory Level Cleaned",
    "Category_Clothing",
    "Category_Electronics",
    "Category_Furniture",
    "Category_Groceries",
    "Category_Toys",
    "Region_East",
    "Region_North",
    "Region_South",
    "Region_West",
    "Weather Condition_Cloudy",
    "Weather Condition_Rainy",
    "Weather Condition_Snowy",
    "Weather Condition_Sunny",
    "Seasonality_Autumn",
    "Seasonality_Spring",
    "Seasonality_Summer",
    "Seasonality_Winter",
    "Year",
    "Day",
}


def load_forecast_model() -> tuple[Any, str, list[str]]:
    """
    Load the first compatible model from MODEL_CANDIDATES.
    Returns: (model, active_model_path, notes)
    """
    errors: list[str] = []
    for model_path in MODEL_CANDIDATES:
        if not model_path.exists():
            continue

        model = joblib.load(model_path)
        model_features = set(getattr(model, "feature_names_in_", []))
        if model_features and not REQUIRED_MODEL_FEATURES.issubset(model_features):
            errors.append(
                f"{model_path} skipped (feature mismatch for current app inputs)"
            )
            continue

        return model, str(model_path), errors

    raise FileNotFoundError(
        "No model file found. Expected one of: "
        + ", ".join(str(path) for path in MODEL_CANDIDATES)
    )

