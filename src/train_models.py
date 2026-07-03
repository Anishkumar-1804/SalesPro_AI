"""
Model Training Script
======================
Trains Prophet, XGBoost, and Linear Regression on the overall daily sales
time series and saves the trained models to /models/.

Run once before starting the Streamlit app:
    python src/train_models.py
"""

import os
import sys
import warnings
import joblib
import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")

# ── Path setup ───────────────────────────────────────────────────────────────
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.data_loader import load_raw, daily_sales
from src.feature_engineering import make_features, FEATURE_COLS
from src.evaluate import evaluate_all

MODELS_DIR = os.path.join(ROOT, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# Train / test split: last 90 days as test
TEST_DAYS = 90


# ─────────────────────────────────────────────────────────────────────────────
# 1. Prophet
# ─────────────────────────────────────────────────────────────────────────────
def train_prophet(ts: pd.Series):
    from prophet import Prophet

    print("  Training Prophet...", end=" ", flush=True)
    df_prophet = pd.DataFrame({"ds": ts.index, "y": ts.values})

    train_df = df_prophet.iloc[:-TEST_DAYS]
    test_df  = df_prophet.iloc[-TEST_DAYS:]

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode="multiplicative",
        changepoint_prior_scale=0.1,
    )
    model.fit(train_df)

    future   = model.make_future_dataframe(periods=TEST_DAYS)
    forecast = model.predict(future)
    y_pred   = forecast.iloc[-TEST_DAYS:]["yhat"].values
    y_true   = test_df["y"].values

    metrics = evaluate_all(y_true, y_pred)
    print(f"done  ->  MAE={metrics['MAE']:.2f}  RMSE={metrics['RMSE']:.2f}  MAPE={metrics['MAPE']:.2f}%")

    joblib.dump({"model": model, "metrics": metrics}, os.path.join(MODELS_DIR, "prophet_model.pkl"))
    return metrics


# ─────────────────────────────────────────────────────────────────────────────
# 2. XGBoost
# ─────────────────────────────────────────────────────────────────────────────
def train_xgboost(ts: pd.Series):
    from xgboost import XGBRegressor

    print("  Training XGBoost...", end=" ", flush=True)
    feat_df = make_features(ts)

    X = feat_df[FEATURE_COLS]
    y = feat_df["y"]

    X_train, X_test = X.iloc[:-TEST_DAYS], X.iloc[-TEST_DAYS:]
    y_train, y_test = y.iloc[:-TEST_DAYS], y.iloc[-TEST_DAYS:]

    model = XGBRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    y_pred  = model.predict(X_test)
    metrics = evaluate_all(y_test, y_pred)
    print(f"done  ->  MAE={metrics['MAE']:.2f}  RMSE={metrics['RMSE']:.2f}  MAPE={metrics['MAPE']:.2f}%")

    joblib.dump({"model": model, "metrics": metrics}, os.path.join(MODELS_DIR, "xgboost_model.pkl"))
    return metrics


# ─────────────────────────────────────────────────────────────────────────────
# 3. Linear Regression (baseline)
# ─────────────────────────────────────────────────────────────────────────────
def train_linear(ts: pd.Series):
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline

    print("  Training Ridge Regression...", end=" ", flush=True)
    feat_df = make_features(ts)

    X = feat_df[FEATURE_COLS]
    y = feat_df["y"]

    X_train, X_test = X.iloc[:-TEST_DAYS], X.iloc[-TEST_DAYS:]
    y_train, y_test = y.iloc[:-TEST_DAYS], y.iloc[-TEST_DAYS:]

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("ridge",  Ridge(alpha=1.0)),
    ])
    model.fit(X_train, y_train)

    y_pred  = model.predict(X_test)
    metrics = evaluate_all(y_test, y_pred)
    print(f"done  ->  MAE={metrics['MAE']:.2f}  RMSE={metrics['RMSE']:.2f}  MAPE={metrics['MAPE']:.2f}%")

    joblib.dump({"model": model, "metrics": metrics}, os.path.join(MODELS_DIR, "linear_model.pkl"))
    return metrics


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n[*] Loading dataset ...")
    df = load_raw()
    ts = daily_sales(df)
    print(f"   Time series: {ts.index[0].date()} -> {ts.index[-1].date()}  ({len(ts)} days)")

    print("\n[*] Training models ...")
    results = {}
    results["Prophet"]           = train_prophet(ts)
    results["XGBoost"]           = train_xgboost(ts)
    results["Ridge Regression"]  = train_linear(ts)

    print("\n[*] Model Comparison:")
    print(f"  {'Model':<20} {'MAE':>8} {'RMSE':>8} {'MAPE':>8} {'R2':>8}")
    print("  " + "-" * 56)
    for name, m in results.items():
        print(f"  {name:<20} {m['MAE']:>8.2f} {m['RMSE']:>8.2f} {m['MAPE']:>7.2f}% {m['R2']:>8.4f}")

    best = min(results, key=lambda k: results[k]["RMSE"])
    print(f"\n[BEST] Best model by RMSE: {best}")
    print("\n[OK] All models saved to /models/\n")

