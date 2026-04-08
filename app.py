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


# Load unique Store IDs and Product IDs from CSV
csv_path = Path("retail_store_inventory.csv")
if csv_path.exists():
    df = pd.read_csv(csv_path)
    unique_store_ids = sorted([str(x) for x in df["Store ID"].dropna().unique().tolist()])
    unique_product_ids = sorted([str(x) for x in df["Product ID"].dropna().unique().tolist()])
else:
    unique_store_ids = []
    unique_product_ids = []

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

st.markdown("---")
with st.expander("Add a daily retail inventory record"):
    st.write(
        "Fill in the daily inventory record details below. Use the buttons to stage records first, then append all staged records to `retail_store_inventory.csv`."
    )

    if "inventory_batch" not in st.session_state:
        st.session_state.inventory_batch = []

    # Initialize session state for form fields
    if "form_date" not in st.session_state:
        st.session_state.form_date = dt.date.today()
    if "store_id" not in st.session_state:
        st.session_state.store_id = unique_store_ids[0] if unique_store_ids else "S001"
    if "product_id" not in st.session_state:
        st.session_state.product_id = unique_product_ids[0] if unique_product_ids else "P0001"
    if "category" not in st.session_state:
        st.session_state.category = "Clothing"
    if "region" not in st.session_state:
        st.session_state.region = "East"
    if "inventory_level" not in st.session_state:
        st.session_state.inventory_level = 0
    if "units_sold" not in st.session_state:
        st.session_state.units_sold = 0
    if "units_ordered" not in st.session_state:
        st.session_state.units_ordered = 0
    if "demand_forecast" not in st.session_state:
        st.session_state.demand_forecast = 0.0
    if "price" not in st.session_state:
        st.session_state.price = 0.0
    if "discount" not in st.session_state:
        st.session_state.discount = 0.0
    if "weather_condition" not in st.session_state:
        st.session_state.weather_condition = "Cloudy"
    if "holiday_promotion" not in st.session_state:
        st.session_state.holiday_promotion = 0
    if "competitor_pricing" not in st.session_state:
        st.session_state.competitor_pricing = 0.0
    if "seasonality" not in st.session_state:
        st.session_state.seasonality = "Autumn"

    with st.form("add_inventory_record"):
        form_date = st.date_input("Date", value=st.session_state.form_date, key="form_date_input")
        store_id = st.text_input("Store ID", value=st.session_state.store_id, key="store_id_input")
        product_id = st.text_input("Product ID", value=st.session_state.product_id, key="product_id_input")
        category = st.selectbox(
            "Category",
            ["Clothing", "Electronics", "Furniture", "Groceries", "Toys"],
            index=["Clothing", "Electronics", "Furniture", "Groceries", "Toys"].index(st.session_state.category),
            key="category_select"
        )
        region = st.selectbox("Region", ["East", "North", "South", "West"],
                              index=["East", "North", "South", "West"].index(st.session_state.region),
                              key="region_select")
        inventory_level = st.number_input("Inventory Level", min_value=0, step=1, value=st.session_state.inventory_level, key="inventory_level_input")
        units_sold = st.number_input("Units Sold", min_value=0, step=1, value=st.session_state.units_sold, key="units_sold_input")
        units_ordered = st.number_input("Units Ordered", min_value=0, step=1, value=st.session_state.units_ordered, key="units_ordered_input")
        demand_forecast = st.number_input(
            "Demand Forecast", min_value=0.0, format="%.2f", value=st.session_state.demand_forecast, key="demand_forecast_input"
        )
        price = st.number_input("Price", min_value=0.0, format="%.2f", value=st.session_state.price, key="price_input")
        discount = st.number_input("Discount", min_value=0.0, format="%.2f", value=st.session_state.discount, key="discount_input")
        weather_condition = st.selectbox(
            "Weather Condition", ["Cloudy", "Rainy", "Snowy", "Sunny"],
            index=["Cloudy", "Rainy", "Snowy", "Sunny"].index(st.session_state.weather_condition),
            key="weather_condition_select"
        )
        holiday_selected = st.selectbox("Holiday/Promotion", ["No", "Yes"],
                                        index=st.session_state.holiday_promotion,
                                        key="holiday_promotion_select")
        holiday_promotion = 1 if holiday_selected == "Yes" else 0
        competitor_pricing = st.number_input(
            "Competitor Pricing", min_value=0.0, format="%.2f", value=st.session_state.competitor_pricing, key="competitor_pricing_input"
        )
        seasonality = st.selectbox(
            "Seasonality", ["Autumn", "Spring", "Summer", "Winter"],
            index=["Autumn", "Spring", "Summer", "Winter"].index(st.session_state.seasonality),
            key="seasonality_select"
        )

        add_to_batch = st.form_submit_button("Add record to batch")

    if add_to_batch:
        # Check for duplicates
        duplicate = any(
            record["Date"] == form_date.strftime("%Y-%m-%d") and
            record["Store ID"] == store_id and
            record["Product ID"] == product_id and
            record["Category"] == category and
            record["Region"] == region
            for record in st.session_state.inventory_batch
        )
        if duplicate:
            st.warning("Duplicate record detected. A record with the same Date, Store ID, Product ID, Category, and Region already exists in the batch.")
        else:
            record = {
                "Date": form_date.strftime("%Y-%m-%d"),
                "Store ID": store_id,
                "Product ID": product_id,
                "Category": category,
                "Region": region,
                "Inventory Level": int(inventory_level),
                "Units Sold": int(units_sold),
                "Units Ordered": int(units_ordered),
                "Demand Forecast": float(demand_forecast),
                "Price": float(price),
                "Discount": float(discount),
                "Weather Condition": weather_condition,
                "Holiday/Promotion": int(holiday_promotion),
                "Competitor Pricing": float(competitor_pricing),
                "Seasonality": seasonality,
            }
            st.session_state.inventory_batch.append(record)
            st.success("Record added to batch. You can add more records or append the batch to CSV.")

            # Reset form fields
            st.session_state.form_date = dt.date.today()
            st.session_state.store_id = "S001"
            st.session_state.product_id = "P0001"
            st.session_state.category = "Clothing"
            st.session_state.region = "East"
            st.session_state.inventory_level = 0
            st.session_state.units_sold = 0
            st.session_state.units_ordered = 0
            st.session_state.demand_forecast = 0.0
            st.session_state.price = 0.0
            st.session_state.discount = 0.0
            st.session_state.weather_condition = "Cloudy"
            st.session_state.holiday_promotion = 0
            st.session_state.competitor_pricing = 0.0
            st.session_state.seasonality = "Autumn"
            st.rerun()  # To refresh the form with reset values

    if st.session_state.inventory_batch:
        st.subheader("Staged Records")
        staged_df = pd.DataFrame(st.session_state.inventory_batch)
        st.dataframe(staged_df, use_container_width=True)

        delete_index = st.selectbox("Select record to delete", range(len(st.session_state.inventory_batch)), 
                                    format_func=lambda x: f"Record {x+1}: {st.session_state.inventory_batch[x]['Date']} - {st.session_state.inventory_batch[x]['Store ID']} - {st.session_state.inventory_batch[x]['Product ID']}")
        if st.button("Delete selected record"):
            del st.session_state.inventory_batch[delete_index]
            st.rerun()

        if st.button("Append all staged records to CSV"):
            csv_path = Path("retail_store_inventory.csv")
            append_header = not csv_path.exists()
            append_df = pd.DataFrame(st.session_state.inventory_batch)
            append_df.to_csv(csv_path, mode="a", header=append_header, index=False)
            st.success(f"Appended {len(append_df)} staged record(s) to `{csv_path}`.")
            st.session_state.inventory_batch = []
    else:
        st.info("No staged records yet. Fill the form and click 'Add record to batch' first.")
