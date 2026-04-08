import datetime as dt
import math
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

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


def load_forecast_model():
    errors = []
    for model_path in MODEL_CANDIDATES:
        if model_path.exists():
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


model, active_model_path, model_notes = load_forecast_model()

st.title("Resource Management Planner")
st.caption("Plan required stock/resources for a selected date or date range.")
st.info(f"Model in use: `{active_model_path}`")
if model_notes:
    st.caption("Model selection notes: " + " | ".join(model_notes))

planning_mode = st.radio("Planning Type", ["Single Date", "Date Range"], horizontal=True)

if planning_mode == "Single Date":
    start_date = st.date_input("Target Date", value=dt.date.today() + dt.timedelta(days=1))
    end_date = start_date
else:
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=dt.date.today() + dt.timedelta(days=1))
    with col2:
        end_date = st.date_input("End Date", value=dt.date.today() + dt.timedelta(days=7))

holiday_promotion = st.selectbox("Holiday/Promotion", [0, 1], help="0 = No, 1 = Yes")
inventory_available = st.number_input("Current Stock Available", min_value=0, step=1)

category = st.selectbox("Category", ["Clothing", "Electronics", "Furniture", "Groceries", "Toys"])
region = st.selectbox("Region", ["East", "North", "South", "West"])
weather_condition = st.selectbox("Weather Condition", ["Cloudy", "Rainy", "Snowy", "Sunny"])
seasonality = st.selectbox("Seasonality", ["Autumn", "Spring", "Summer", "Winter"])

if st.button("Calculate Resource Plan"):
    if end_date < start_date:
        st.error("End Date cannot be before Start Date.")
        st.stop()

    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    rows = []
    current_stock_balance = int(inventory_available)

    for target_day in date_range:
        input_dict = {
            "Month": int(target_day.month),
            "Holiday/Promotion": holiday_promotion,
            "Inventory Level Cleaned": inventory_available,
            "Category_Clothing": 0,
            "Category_Electronics": 0,
            "Category_Furniture": 0,
            "Category_Groceries": 0,
            "Category_Toys": 0,
            "Region_East": 0,
            "Region_North": 0,
            "Region_South": 0,
            "Region_West": 0,
            "Weather Condition_Cloudy": 0,
            "Weather Condition_Rainy": 0,
            "Weather Condition_Snowy": 0,
            "Weather Condition_Sunny": 0,
            "Seasonality_Autumn": 0,
            "Seasonality_Spring": 0,
            "Seasonality_Summer": 0,
            "Seasonality_Winter": 0,
            "Year": int(target_day.year),
            "Day": int(target_day.day),
        }

        input_dict[f"Category_{category}"] = 1
        input_dict[f"Region_{region}"] = 1
        input_dict[f"Weather Condition_{weather_condition}"] = 1
        input_dict[f"Seasonality_{seasonality}"] = 1

        input_df = pd.DataFrame([input_dict])
        model_columns = getattr(model, "feature_names_in_", None)
        if model_columns is not None:
            input_df = input_df.reindex(columns=model_columns, fill_value=0)

        expected_usage = max(int(math.ceil(float(model.predict(input_df)[0]))), 0)
        current_stock = current_stock_balance
        closing_stock = current_stock_balance - expected_usage
        current_stock_balance = closing_stock
        stock_status = "Shortage" if closing_stock < 0 else "Available"

        rows.append(
            {
                "Date": target_day.date(),
                "Expected Usage": expected_usage,
                "Current Stock": current_stock,
                "Closing Stock": closing_stock,
                "Stock Status": stock_status,
            }
        )

    result_df = pd.DataFrame(rows)
    result_df["Total Usage Till Date"] = result_df["Expected Usage"].cumsum()
    total_resource_needed = int(result_df["Expected Usage"].sum())
    additional_stock_needed = max(total_resource_needed - int(inventory_available), 0)

    st.subheader("Resource Forecast Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Resource Needed", f"{total_resource_needed:,}")
    col2.metric("Current Stock", f"{int(inventory_available):,}")
    col3.metric("Additional Stock Needed", f"{additional_stock_needed:,}")

    if additional_stock_needed > 0:
        st.warning(f"Stock is short by {additional_stock_needed:,} units for the selected period.")
    else:
        st.success("Current stock is sufficient for the selected period.")

    st.subheader("Current vs Forecast View")
    st.dataframe(
        result_df[["Date", "Current Stock", "Expected Usage", "Closing Stock"]].style.format(
            {
                "Current Stock": "{:,.0f}",
                "Expected Usage": "{:,.0f}",
                "Closing Stock": "{:,.0f}",
            }
        ),
        use_container_width=True,
    )

    st.subheader("Detailed Resource and Stock Plan")
    st.dataframe(
        result_df.style.format(
            {
                "Expected Usage": "{:,.0f}",
                "Current Stock": "{:,.0f}",
                "Closing Stock": "{:,.0f}",
                "Total Usage Till Date": "{:,.0f}",
            }
        ),
        use_container_width=True,
    )
