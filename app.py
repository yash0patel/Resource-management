import pandas as pd
import joblib
import streamlit as st

# Load model
model = joblib.load("best_sales_model.joblib")

st.header("Inventory Prediction")

# Input fields
Month = st.selectbox("Month", list(range(1, 13)))
Holiday_Promotion = st.selectbox("Holiday/Promotion", [0, 1])
Inventory_Level_Cleaned = st.number_input("Inventory Available", min_value=0)
Year = st.selectbox("Year", [2023, 2024, 2025])
Day = st.selectbox("Day", list(range(1, 32)))

# New dropdowns
Category = st.selectbox("Category", ["Clothing", "Electronics", "Furniture", "Groceries", "Toys"])
Region = st.selectbox("Region", ["East", "North", "South", "West"])
Weather_Condition = st.selectbox("Weather Condition", ["Cloudy", "Rainy", "Snowy", "Sunny"])
Seasonality = st.selectbox("Seasonality", ["Autumn", "Spring", "Summer", "Winter"])

# Prepare input for prediction
if st.button("Predict"):
    # Create a dict with default 0s for one-hot columns
    input_dict = {
        'Month': Month,
        'Holiday/Promotion': Holiday_Promotion,
        'Inventory Level Cleaned': Inventory_Level_Cleaned,
        'Category_Clothing': 0,
        'Category_Electronics': 0,
        'Category_Furniture': 0,
        'Category_Groceries': 0,
        'Category_Toys': 0,
        'Region_East': 0,
        'Region_North': 0,
        'Region_South': 0,
        'Region_West': 0,
        'Weather Condition_Cloudy': 0,
        'Weather Condition_Rainy': 0,
        'Weather Condition_Snowy': 0,
        'Weather Condition_Sunny': 0,
        'Seasonality_Autumn': 0,
        'Seasonality_Spring': 0,
        'Seasonality_Summer': 0,
        'Seasonality_Winter': 0,
        'Year': Year,
        'Day': Day
    }

    # Set selected category, region, weather, seasonality to 1
    input_dict[f"Category_{Category}"] = 1
    input_dict[f"Region_{Region}"] = 1
    input_dict[f"Weather Condition_{Weather_Condition}"] = 1
    input_dict[f"Seasonality_{Seasonality}"] = 1

    # Convert dict to DataFrame
    input_df = pd.DataFrame([input_dict])

    # Predict
    output = model.predict(input_df)
    st.success(f"The predicted sales is: ${output[0]:.2f}")