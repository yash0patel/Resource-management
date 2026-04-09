import datetime as dt
import math
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Inventory Management System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit Branding
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Custom CSS for better UI
st.markdown("""
    <style>
        :root {
            --primary-color: #1e3c72;
            --secondary-color: #2a5298;
            --accent-color: #00d4ff;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --danger-color: #ef4444;
            --light-bg: #f8fafc;
            --border-color: #e2e8f0;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body, html {
            background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
            background-attachment: fixed;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
        }
        
        .main {
            background: transparent !important;
            padding: 0 !important;
        }
        
        [data-testid="stMain"] {
            background: transparent;
        }
        
        /* Navbar */
        .navbar {
            background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            padding: 1rem 2rem;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
            margin-bottom: 2rem;
            border-bottom: 4px solid var(--accent-color);
            position: sticky;
            top: 0;
            z-index: 1000;
            border-radius: 0 0 12px 12px;
        }
        
        .navbar-content {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .navbar-brand {
            color: white;
            font-size: 1.5rem;
            font-weight: 800;
            letter-spacing: 1px;
        }
        
        .navbar-subtitle {
            color: var(--accent-color);
            font-size: 0.85rem;
            margin-left: 12px;
            font-weight: 600;
        }
        
        /* Header Container */
        .header-container {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 50%, #1a2a5a 100%);
            padding: 3.5rem 2rem;
            border-radius: 16px;
            margin: 0 auto 3rem;
            max-width: 1400px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.15);
            position: relative;
            overflow: hidden;
        }
        
        .header-container::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(0, 212, 255, 0.1) 0%, transparent 70%);
            animation: float 6s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(20px); }
        }
        
        .header-title {
            color: white;
            font-size: 2.8rem;
            font-weight: 900;
            margin: 0 0 0.5rem 0;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.4);
            letter-spacing: 0.5px;
            position: relative;
            z-index: 1;
        }
        
        .header-subtitle {
            color: var(--accent-color);
            font-size: 1.1rem;
            margin: 0;
            font-weight: 500;
            position: relative;
            z-index: 1;
        }
        
        /* Main Container */
        .main-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 1rem;
        }
        
        /* Tabs Styling */
        .stTabs {
            margin-bottom: 2rem;
        }
        
        .stTabs [data-baseweb='tabs'] {
            background-color: transparent;
        }
        
        .stTabs [role='tablist'] {
            background-color: white;
            border: 2px solid var(--border-color);
            border-radius: 12px 12px 0 0;
            padding: 0.5rem;
            gap: 0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            display: flex;
            justify-content: flex-start;
        }
        
        .stTabs [role='tab'] {
            padding: 0.9rem 1.8rem;
            color: #666;
            font-weight: 700;
            font-size: 1rem;
            border-radius: 8px;
            background-color: transparent;
            border: 2px solid transparent;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stTabs [role='tab']:hover {
            background-color: rgba(30, 60, 114, 0.05);
        }
        
        .stTabs [role='tab'][aria-selected='true'] {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(30, 60, 114, 0.3);
        }
        
        .stTabs [role='tabpanel'] {
            background: white;
            border: 2px solid var(--border-color);
            border-radius: 0 12px 12px 12px;
            padding: 2.5rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }
        
        /* Info Box */
        .info-box {
            background: linear-gradient(135deg, #e0f2f1 0%, #b2dfdb 100%);
            border-left: 5px solid var(--success-color);
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
            color: #0f6b45;
        }
        
        /* Section Container */
        .section-container {
            background: white;
            padding: 2.5rem;
            border-radius: 14px;
            border-left: 6px solid var(--primary-color);
            margin-bottom: 2.5rem;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
            border-top: 1px solid var(--border-color);
            transition: all 0.3s ease;
        }
        
        .section-container:hover {
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
        }
        
        .section-title {
            color: var(--primary-color);
            font-size: 1.8rem;
            font-weight: 900;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 3px solid var(--accent-color);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Form Styling */
        .stForm {
            background: transparent;
            padding: 0;
        }
        
        [data-testid="stForm"] {
            border: none;
        }
        
        .stForm label, label {
            color: var(--primary-color) !important;
            font-weight: 700 !important;
            font-size: 0.95rem !important;
            text-transform: uppercase;
            letter-spacing: 0.3px;
            margin-bottom: 0.5rem !important;
        }
        
        .stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox select {
            border: 2px solid var(--border-color) !important;
            border-radius: 8px !important;
            padding: 0.9rem !important;
            font-size: 1rem !important;
            background-color: #fafbfc !important;
            transition: all 0.3s ease !important;
            font-weight: 500 !important;
        }
        
        .stTextInput input:focus, .stNumberInput input:focus, .stDateInput input:focus, .stSelectbox select:focus {
            border-color: var(--accent-color) !important;
            box-shadow: 0 0 0 4px rgba(0, 212, 255, 0.15) !important;
            background-color: white !important;
        }
        
        .stSelectbox {
            margin-bottom: 1.5rem;
        }
        
        /* Button Styling */
        .stButton > button {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            border: none;
            padding: 1rem 2.5rem;
            border-radius: 10px;
            font-weight: 800;
            font-size: 0.95rem;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 6px 20px rgba(30, 60, 114, 0.3);
            text-transform: uppercase;
            letter-spacing: 1px;
            width: 100%;
        }
        
        .stButton > button:hover {
            box-shadow: 0 8px 30px rgba(30, 60, 114, 0.5);
            transform: translateY(-3px);
        }
        
        .stButton > button:active {
            transform: translateY(-1px);
        }
        
        /* Metrics */
        .metric-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        [data-testid="metric.container"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            border-radius: 14px !important;
            padding: 2rem !important;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.25) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            transition: all 0.3s ease;
        }
        
        [data-testid="metric.container"]:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 35px rgba(102, 126, 234, 0.35) !important;
        }
        
        [data-testid="metric.label"], [data-testid="metric.value"] {
            color: white !important;
        }
        
        /* Dataframe */
        .stDataframe {
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            overflow: hidden;
        }
        
        /* Success/Warning/Error/Info Messages */
        .stSuccess, .stWarning, .stError, .stInfo {
            border-radius: 10px !important;
            padding: 1.2rem !important;
            border-left: 5px solid !important;
            font-weight: 600;
        }
        
        .stSuccess {
            background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%) !important;
            border-left-color: var(--success-color) !important;
            color: #166534 !important;
        }
        
        .stWarning {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%) !important;
            border-left-color: var(--warning-color) !important;
            color: #92400e !important;
        }
        
        .stError {
            background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%) !important;
            border-left-color: var(--danger-color) !important;
            color: #7f1d1d !important;
        }
        
        .stInfo {
            background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%) !important;
            border-left-color: #0284c7 !important;
            color: #0c2d6b !important;
        }
        
        /* Radio Button */
        .stRadio {
            background: white;
            padding: 1.2rem;
            border-radius: 10px;
            border: 2px solid var(--border-color);
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }
        
        /* Divider */
        hr {
            border-color: var(--border-color) !important;
            margin: 2rem 0 !important;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, #f8fafc 0%, #e8eef5 100%) !important;
            border-radius: 10px !important;
            border: 2px solid var(--border-color) !important;
            padding: 1rem !important;
            font-weight: 700 !important;
            color: var(--primary-color) !important;
        }
        
        /* Footer */
        .footer-container {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            padding: 3rem 2rem;
            border-radius: 16px;
            margin-top: 3rem;
            text-align: center;
            border-top: 4px solid var(--accent-color);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            color: white;
        }
        
        .footer-text {
            color: white;
            font-size: 1rem;
            margin: 0.7rem 0;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .footer-text-small {
            font-size: 0.85rem;
            margin-top: 1.5rem;
            color: var(--accent-color);
            opacity: 0.95;
            font-weight: 500;
        }
        
        /* Title Styling */
        h1, h2, h3, h4, h5, h6 {
            color: var(--primary-color) !important;
        }
        
        p {
            color: #4a5568;
            line-height: 1.7;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(135deg, #f8fafc 0%, #e8eef5 100%);
            border-right: 2px solid var(--border-color);
        }
        
        /* General Text Color Fix */
        body, p, span, label {
            color: #333 !important;
        }
        
        .stMarkdown, .stCaption {
            color: #333 !important;
        }
    </style>
""", unsafe_allow_html=True)

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

# Header Section
st.markdown("""
    <div class="navbar">
        <div class="navbar-content">
            <div>
                <span class="navbar-brand">📦 IMS</span>
                <span class="navbar-subtitle">Inventory Management System</span>
            </div>
        </div>
    </div>
    <div class="main-container">
        <div class="header-container">
            <h1 class="header-title">📦 Inventory Management System</h1>
            <p class="header-subtitle">🚀 AI-Powered Forecasting & Retail Optimization</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Info box
st.markdown(f"""
    <div class="main-container">
        <div class="info-box">
            <strong>🤖 Active Model:</strong> <code>{active_model_path}</code><br>
            <strong>✓ Status:</strong> Model validation passed
        </div>
    </div>
""", unsafe_allow_html=True)

# Navigation/Tabs
st.markdown('<div class="main-container">', unsafe_allow_html=True)
tab1, tab2 = st.tabs(["📊 Forecast Planner", "📝 Add Records"])
st.markdown('</div>', unsafe_allow_html=True)

with tab1:
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-container"><div class="section-title">📊 Resource Forecast Planner</div>', unsafe_allow_html=True)
    
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

        st.subheader("💰 Resource Forecast Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            col1.metric("📊 Total Resource Needed", f"{total_resource_needed:,}")
        with col2:
            col2.metric("📦 Current Stock", f"{int(inventory_available):,}")
        with col3:
            col3.metric("⚠️ Additional Needed", f"{additional_stock_needed:,}")

        if additional_stock_needed > 0:
            st.warning(f"Stock is short by {additional_stock_needed:,} units for the selected period.")
        else:
            st.success("Current stock is sufficient for the selected period.")

        st.subheader("📊 Current vs Forecast View")
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

        st.subheader("📈 Detailed Resource and Stock Plan")
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
    
    st.markdown('</div></div>', unsafe_allow_html=True)  # Close section and main container

with tab2:
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-container"><div class="section-title">📝 Add Inventory Records</div>', unsafe_allow_html=True)
    st.write(
        "Fill in the daily inventory record details below. Use the buttons to stage records first, then append all staged records to the CSV file."
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
        st.subheader("📋 Staged Records - Ready to Upload")
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
    
    st.markdown('</div></div>', unsafe_allow_html=True)  # Close section and main container

# Footer Section
st.markdown("""
    <div class="main-container">
        <div class="footer-container">
            <p class="footer-text"><strong>📦 Inventory Management System v1.0</strong></p>
            <p class="footer-text">Intelligent Forecasting | Data-Driven Decisions | ML-Powered Analytics</p>
            <p class="footer-text-small">🎓 College Project | Built with Python & Streamlit | © 2026</p>
        </div>
    </div>
""", unsafe_allow_html=True)
