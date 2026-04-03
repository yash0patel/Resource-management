import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import joblib
import os
from utils import load_data, preprocess_data, get_historical_volatility

os.makedirs('models', exist_ok=True)

def train_v3():
    # 1. Loading & Initial Processing
    print("[1/6] Loading historical dataset...")
    df = load_data('data/retail_store_inventory.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(['Store ID', 'Product ID', 'Date'])
    
    # 2. Advanced Feature Engineering (Lags)
    print("[2/6] Engineering Lag Features (Memory)...")
    # Capturing 1-day lag to teach the model 'continuity'
    df['Prev_Demand'] = df.groupby(['Store ID', 'Product ID'])['Units Sold'].shift(1)
    df.bfill(inplace=True) # Minimal backfill for the first records
    
    # Preprocess (Removing Region and adding Cyclical features)
    df_processed, encoders = preprocess_data(df, is_training=True)
    
    # Save historical volatility for the app
    vol_stats = get_historical_volatility(df)
    joblib.dump(vol_stats, 'models/volatility_stats.joblib')

    # 3. Features Selection (v3 Precision Set)
    target = 'Units Sold'
    features = [
        'Month_sin', 'Month_cos', 'Day_sin', 'Day_cos', 'DayOfWeek_sin', 'DayOfWeek_cos',
        'Store ID', 'Product ID', 'Category', 'Inventory Level', 'Price', 'Discount',
        'Weather Condition', 'Holiday/Promotion', 'Competitor Pricing', 'Seasonality',
        'Prev_Demand'
    ]
    
    X = df_processed[features]
    y = df_processed[target]
    
    # 4. Temporal Splitting
    split_idx = int(len(df_processed) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    # 5. Advanced Model Training
    print("[3/6] Fitting Graduate-Level Models...")
    models = {
        "RandomForest_Tuned": RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42),
        "GradientBoosting": GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    }
    
    best_model = None
    best_r2 = -1
    
    for name, model in models.items():
        print(f"   -> Training {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        print(f"      R2 Accuracy: {r2:.4f}")
        
        if r2 > best_r2:
            best_r2 = r2
            best_model = model
            
    # 6. Serialization
    print(f"[4/6] Exporting engine (Best R2: {best_r2:.4f})...")
    joblib.dump(best_model, 'models/best_resource_model.joblib')
    joblib.dump(features, 'models/feature_names.joblib')
    
    print("[5/6] Model Sync Complete!")

if __name__ == "__main__":
    train_v3()
