# Sales Prediction System - Detailed Documentation

## 1. What This Project Does

This project is a **Streamlit-based Resource Management Planner** that predicts expected daily resource/sales usage using a trained machine learning model and converts that forecast into a stock planning report.

In simple terms, you provide:
- date (single day or date range),
- inventory currently available,
- product category,
- region,
- weather condition,
- season,
- holiday/promotion flag.

The app predicts expected usage and shows:
- daily expected usage,
- current stock vs closing stock,
- shortage/availability status,
- total usage for selected period,
- additional stock needed.

---

## 2. Project Structure

```text
Sales_Prediction_System/
|-- app.py                           # Main Streamlit application
|-- app2.py                          # Thin wrapper importing app.py
|-- models/
|   |-- best_resource_model.joblib   # Preferred model
|   |-- encoders.joblib              # Training artifact (not used by runtime app)
|   |-- feature_names.joblib         # Training artifact
|   |-- volatility_stats.joblib      # Training artifact
|-- best_sales_model.joblib          # Fallback model
|-- Sales_model.pkl                  # Final fallback model
|-- retail_store_inventory.csv       # Raw dataset
|-- combined.csv                     # Processed dataset (one-hot encoded columns)
|-- combined2.csv                    # Another processed dataset variant
|-- Predict sale.ipynb               # Notebook used for model experimentation/training
```

---

## 3. Main Code Overview (`app.py`)

### 3.1 Imports
- `datetime` for default date values.
- `math` for ceiling operation on model prediction.
- `pathlib.Path` for model file paths.
- `joblib` for loading persisted sklearn models.
- `pandas` for tabular input/output handling.
- `streamlit` for web UI.

### 3.2 Model Selection Strategy
The app defines model candidates in this order:
1. `models/best_resource_model.joblib`
2. `best_sales_model.joblib`
3. `Sales_model.pkl`

The first existing model is loaded, but if it has `feature_names_in_`, the app validates it contains required input features.  
If features mismatch, that model is skipped and the next candidate is tried.

This makes the app robust against incompatible model files.

### 3.3 Required Features
The app expects 22 features:
- Time: `Month`, `Year`, `Day`
- Context: `Holiday/Promotion`, `Inventory Level Cleaned`
- One-hot category: `Category_Clothing`, `Category_Electronics`, `Category_Furniture`, `Category_Groceries`, `Category_Toys`
- One-hot region: `Region_East`, `Region_North`, `Region_South`, `Region_West`
- One-hot weather: `Weather Condition_Cloudy`, `Weather Condition_Rainy`, `Weather Condition_Snowy`, `Weather Condition_Sunny`
- One-hot seasonality: `Seasonality_Autumn`, `Seasonality_Spring`, `Seasonality_Summer`, `Seasonality_Winter`

### 3.4 UI Inputs
The app takes:
- planning type: single date / date range,
- target/start/end date,
- holiday/promotion (`0` or `1`),
- current stock available,
- category,
- region,
- weather condition,
- seasonality.

### 3.5 Forecast and Stock Logic
When user clicks **Calculate Resource Plan**:
1. Validate end date is not before start date.
2. Build daily rows over selected date range.
3. Build one feature vector per day.
4. Set selected category/region/weather/season one-hot column to 1.
5. Reindex input columns to model feature order (if model provides names).
6. Predict daily usage using model.
7. Apply:
   - `expected_usage = max(ceil(prediction), 0)`
8. Update rolling stock balance:
   - `closing_stock = current_stock - expected_usage`
9. Mark status:
   - `"Shortage"` if closing stock < 0 else `"Available"`.

### 3.6 Outputs Shown
- **Summary metrics**
  - Total Resource Needed
  - Current Stock
  - Additional Stock Needed
- **Current vs Forecast View** table
  - Date, Current Stock, Expected Usage, Closing Stock
- **Detailed Resource and Stock Plan** table
  - Includes cumulative usage (`Total Usage Till Date`)

---

## 4. Secondary File (`app2.py`)

`app2.py` contains:

```python
from app import *  # noqa: F401,F403
```

It simply re-exports the main app module. Running `streamlit run app2.py` effectively runs the same app as `app.py`.

---

## 5. Models Used in Runtime

Detected model types:
- `models/best_resource_model.joblib` -> `GradientBoostingRegressor`
- `best_sales_model.joblib` -> `GradientBoostingRegressor`
- `Sales_model.pkl` -> `RandomForestRegressor`

All expose compatible `feature_names_in_` with 22 features expected by app.

---

## 6. Data Files

### `retail_store_inventory.csv` (raw)
Contains columns like:
- Date, Store ID, Product ID, Category, Region,
- Inventory Level, Units Sold, Units Ordered, Demand Forecast,
- Price, Discount, Weather Condition, Holiday/Promotion, Competitor Pricing, Seasonality.

### `combined.csv` / `combined2.csv` (processed)
Contain model-ready columns with one-hot encoded variables and cleaned inventory field.

These CSV files are not directly read by `app.py` during runtime; they support training/analysis workflows.

---

## 7. How to Run the Project

## 7.1 Prerequisites
- Python 3.10+ recommended
- pip

### 7.2 Install Dependencies
Run in project folder:

```bash
pip install streamlit pandas joblib scikit-learn
```

### 7.3 Start the App

```bash
streamlit run app.py
```

If `streamlit` is not recognized:

```bash
python -m streamlit run app.py
```

---

## 8. End-to-End Runtime Flow

1. App starts and loads first valid model from fallback list.
2. User selects planning inputs.
3. App creates one row per day in selected period.
4. Model predicts daily usage.
5. App computes rolling stock depletion and shortages.
6. App presents summary and detailed tables for procurement decisions.

---

## 9. Error Handling and Behavior Notes

- If no model file exists in candidate list, app raises `FileNotFoundError`.
- If a model exists but feature schema is incompatible, app skips it and tries next model.
- Negative predictions are clipped to zero after ceiling.
- Date range validation prevents invalid intervals.

---

## 10. Known Limitations

- No explicit `requirements.txt` or pinned environment lockfile.
- Model was trained in a different sklearn version than one environment tested against, which can show `InconsistentVersionWarning` for old pickle artifacts.
- App assumes same static context (category/region/weather/season/inventory input) across all days in selected range.
- No authentication or multi-user persistence.

---

## 11. Suggested Improvements

1. Add `requirements.txt` with pinned versions.
2. Add a training script and formal model versioning metadata.
3. Add unit tests for feature-building and stock-balance logic.
4. Add CSV export of forecast table.
5. Add charts (daily usage, stock trajectory, shortage points).
6. Add input validation ranges for practical business constraints.

---

## 12. Quick Usage Example

Example scenario:
- Date Range: next 7 days
- Current Stock: 500
- Category: Electronics
- Region: North
- Weather: Rainy
- Seasonality: Summer
- Holiday/Promotion: 1

The app predicts day-wise usage, subtracts it from stock daily, and tells whether more stock is needed and by how much.

---

## 13. One-Line Summary

This is an ML-powered Streamlit planner that converts contextual retail inputs into a date-wise resource forecast and stock shortage plan.
