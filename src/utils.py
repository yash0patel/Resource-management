import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import joblib
import os

def load_data(file_path='data/retail_store_inventory.csv'):
    """Load the dataset."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found at {file_path}")
    return pd.read_csv(file_path)

def preprocess_data(df, is_training=True):
    """
    Advanced preprocessing with Cyclical Encoding and simplified features.
    """
    df = df.copy()
    df.columns = [col.strip() for col in df.columns]
    
    # 1. Date Features
    df['Date'] = pd.to_datetime(df['Date'])
    
    # --- Cyclical Encoding (Capturing circular nature of time) ---
    # Month (1-12)
    df['Month_sin'] = np.sin(2 * np.pi * df['Date'].dt.month / 12)
    df['Month_cos'] = np.cos(2 * np.pi * df['Date'].dt.month / 12)
    
    # Day (1-31)
    df['Day_sin'] = np.sin(2 * np.pi * df['Date'].dt.day / 31)
    df['Day_cos'] = np.cos(2 * np.pi * df['Date'].dt.day / 31)
    
    # DayOfWeek (0-6)
    df['DayOfWeek_sin'] = np.sin(2 * np.pi * df['Date'].dt.dayofweek / 7)
    df['DayOfWeek_cos'] = np.cos(2 * np.pi * df['Date'].dt.dayofweek / 7)
    
    # 2. Categorical Encoding (Removed Region)
    categorical_cols = ['Store ID', 'Product ID', 'Category', 'Weather Condition', 'Seasonality']
    
    encoders = {}
    if is_training:
        for col in categorical_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
        joblib.dump(encoders, 'models/encoders.joblib')
    else:
        if os.path.exists('models/encoders.joblib'):
            encoders = joblib.load('models/encoders.joblib')
            for col in categorical_cols:
                if col in encoders:
                    df[col] = df[col].apply(lambda x: encoders[col].transform([x])[0] if x in encoders[col].classes_ else 0)
    
    return df, encoders

def get_historical_volatility(df):
    """
    Calculates historical standard deviation of demand per product.
    Used for a more genuine 'Scientific Safety Stock'.
    """
    stats = df.groupby('Product ID')['Units Sold'].agg(['mean', 'std']).reset_index()
    stats.fillna(0, inplace=True)
    return stats

def calculate_precision_resources(daily_demands, historical_std=None, current_inventory=None):
    """
    Professional-grade Resource Logic using Confidence Intervals.
    """
    demands = np.array(daily_demands)
    mean_demand = np.mean(demands)
    total_demand = int(np.sum(demands))
    peak_demand = np.max(demands)
    
    # 1. Scientific Safety Stock
    # Instead of a flat 15%, we use: Mean + (Service Level Z * StdDev)
    # Average StdDev across dataset is used if specific product std is unavailable
    service_factor = 1.96 # 95% Confidence interval
    variability_buffer = (historical_std if historical_std is not None else mean_demand * 0.2) * service_factor
    
    # Total optimal stock for the period
    inventory_target = int(np.round(total_demand + variability_buffer))
    
    # 2. Strategic Workforce Planning
    # 1 staff per 45 units (high precision ratio)
    optimal_staff = max(1, int(np.round(peak_demand / 45)))
    
    # 3. Capital Exposure & Storage
    capital_at_risk = "Surplus" if current_inventory is not None and current_inventory > inventory_target else "Balanced"
    storage_needs = np.round(peak_demand * 0.55, 2)
    
    # Detailed Risk Assessment
    risk_score = "Optimized"
    action = "Continue standard operations."
    
    if current_inventory is not None:
        if current_inventory < total_demand:
            risk_score = "High / Understock"
            action = f"REPLENISHMENT REQUIRED: Procure {total_demand - current_inventory} units to meet core demand."
        elif current_inventory < inventory_target:
            risk_score = "Medium / Service Risk"
            action = "INVENTORY LOW: Buffer stock is depleted. Order small batch to cover volatility."
        elif current_inventory > inventory_target * 1.8:
            risk_score = "High / Overstock"
            action = "LIQUIDITY ALERT: High capital locked in surplus stock. Review discounting strategies."
            
    return {
        "forecasted_demand": total_demand,
        "peak_demand": int(peak_demand),
        "inventory_target": inventory_target,
        "optimal_workforce": optimal_staff,
        "storage_requirement": storage_needs,
        "risk_assessment": risk_score,
        "action_plan": action
    }
