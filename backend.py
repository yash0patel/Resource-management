from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import joblib
import pandas as pd
import math
import datetime as dt
from typing import List, Dict, Optional

# Initialize FastAPI app
app = FastAPI(title="Inventory Management API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model loading
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
    """Load the ML model from available candidates"""
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

# Load model and data
try:
    model, active_model_path, model_notes = load_forecast_model()
except FileNotFoundError as e:
    model = None
    active_model_path = "No model loaded"
    model_notes = [str(e)]

# Load CSV data
csv_path = Path("retail_store_inventory.csv")
if csv_path.exists():
    df = pd.read_csv(csv_path)
    unique_store_ids = sorted([str(x) for x in df["Store ID"].dropna().unique().tolist()])
    unique_product_ids = sorted([str(x) for x in df["Product ID"].dropna().unique().tolist()])
else:
    unique_store_ids = []
    unique_product_ids = []

# Pydantic Models
class ForecastRequest(BaseModel):
    """Request model for forecast prediction"""
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    holiday_promotion: int
    inventory_available: int
    category: str
    region: str
    weather_condition: str
    seasonality: str

class InventoryRecord(BaseModel):
    """Model for inventory record"""
    date: str
    store_id: str
    product_id: str
    category: str
    region: str
    inventory_level: int
    units_sold: int
    units_ordered: int
    demand_forecast: float
    price: float
    discount: float
    weather_condition: str
    holiday_promotion: int
    competitor_pricing: float
    seasonality: str

class BatchAddRequest(BaseModel):
    """Request to add batch records"""
    records: List[InventoryRecord]

# Routes
@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "model_status": "loaded" if model else "not_loaded",
        "active_model": active_model_path
    }

@app.get("/api/stats")
def get_stats():
    """Get initial statistics for dashboard"""
    if not csv_path.exists():
        return {
            "total_records": 0,
            "unique_stores": 0,
            "unique_products": 0,
            "date_range": None
        }
    
    df = pd.read_csv(csv_path)
    return {
        "total_records": len(df),
        "unique_stores": df["Store ID"].nunique() if "Store ID" in df.columns else 0,
        "unique_products": df["Product ID"].nunique() if "Product ID" in df.columns else 0,
        "date_range": {
            "start": df["Date"].min() if "Date" in df.columns else None,
            "end": df["Date"].max() if "Date" in df.columns else None,
        }
    }

@app.post("/api/forecast")
def forecast(request: ForecastRequest):
    """Generate forecast for inventory"""
    if not model:
        raise HTTPException(status_code=400, detail="Model not loaded")
    
    try:
        start_date = dt.datetime.strptime(request.start_date, "%Y-%m-%d").date()
        end_date = dt.datetime.strptime(request.end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="End date cannot be before start date")
    
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    rows = []
    current_stock_balance = request.inventory_available

    for target_day in date_range:
        input_dict = {
            "Month": int(target_day.month),
            "Holiday/Promotion": request.holiday_promotion,
            "Inventory Level Cleaned": request.inventory_available,
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

        input_dict[f"Category_{request.category}"] = 1
        input_dict[f"Region_{request.region}"] = 1
        input_dict[f"Weather Condition_{request.weather_condition}"] = 1
        input_dict[f"Seasonality_{request.seasonality}"] = 1

        input_df = pd.DataFrame([input_dict])
        model_columns = getattr(model, "feature_names_in_", None)
        if model_columns is not None:
            input_df = input_df.reindex(columns=model_columns, fill_value=0)

        expected_usage = max(int(math.ceil(float(model.predict(input_df)[0]))), 0)
        current_stock = current_stock_balance
        closing_stock = current_stock_balance - expected_usage
        current_stock_balance = closing_stock
        stock_status = "Shortage" if closing_stock < 0 else "Available"

        rows.append({
            "date": target_day.date().isoformat(),
            "expected_usage": expected_usage,
            "current_stock": current_stock,
            "closing_stock": closing_stock,
            "stock_status": stock_status,
        })

    result_df = pd.DataFrame(rows)
    result_df["total_usage_till_date"] = result_df["expected_usage"].cumsum().tolist()
    total_resource_needed = int(result_df["expected_usage"].sum())
    additional_stock_needed = max(total_resource_needed - request.inventory_available, 0)

    return {
        "summary": {
            "total_resource_needed": total_resource_needed,
            "current_stock": request.inventory_available,
            "additional_needed": additional_stock_needed,
        },
        "forecast": result_df.to_dict(orient="records"),
    }

@app.get("/api/dropdowns")
def get_dropdowns():
    """Get dropdown options"""
    return {
        "categories": ["Clothing", "Electronics", "Furniture", "Groceries", "Toys"],
        "regions": ["East", "North", "South", "West"],
        "weather_conditions": ["Cloudy", "Rainy", "Snowy", "Sunny"],
        "seasonalities": ["Autumn", "Spring", "Summer", "Winter"],
        "store_ids": unique_store_ids,
        "product_ids": unique_product_ids,
    }

@app.post("/api/add-records")
def add_records(request: BatchAddRequest):
    """Add records to CSV"""
    try:
        csv_path = Path("retail_store_inventory.csv")
        append_header = not csv_path.exists()
        
        # Convert records to DataFrame
        data = [record.dict() for record in request.records]
        df_to_append = pd.DataFrame(data)
        
        # Rename columns to match CSV format
        df_to_append = df_to_append.rename(columns={
            "date": "Date",
            "store_id": "Store ID",
            "product_id": "Product ID",
            "category": "Category",
            "region": "Region",
            "inventory_level": "Inventory Level",
            "units_sold": "Units Sold",
            "units_ordered": "Units Ordered",
            "demand_forecast": "Demand Forecast",
            "price": "Price",
            "discount": "Discount",
            "weather_condition": "Weather Condition",
            "holiday_promotion": "Holiday/Promotion",
            "competitor_pricing": "Competitor Pricing",
            "seasonality": "Seasonality",
        })
        
        df_to_append.to_csv(csv_path, mode="a", header=append_header, index=False)
        
        return {
            "status": "success",
            "message": f"Added {len(request.records)} records",
            "count": len(request.records)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
