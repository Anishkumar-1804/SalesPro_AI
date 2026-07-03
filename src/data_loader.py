"""
Data Loader & Preprocessor
===========================
Loads train.csv (Indian e-commerce dataset), cleans it,
and returns ready-to-use DataFrames.

Dataset modeled after:
  Amazon Sales Report (India) — Kaggle
  https://www.kaggle.com/datasets/thedevastator/unlock-profits-with-e-commerce-sales-data
"""

import pandas as pd
import numpy as np
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "train.csv")

# Column aliases for flexibility
SALES_COL  = "Sales (INR)"
PROFIT_COL = "Profit (INR)"


def load_raw() -> pd.DataFrame:
    """Load raw CSV and parse dates."""
    df = pd.read_csv(DATA_PATH, parse_dates=["Order Date"])
    df.sort_values("Order Date", inplace=True)
    df.reset_index(drop=True, inplace=True)
    # Only delivered/shipped orders count as revenue
    df = df[df["Order Status"].isin(["Delivered", "Shipped"])].copy()
    return df


def daily_sales(df: pd.DataFrame, category: str = "All", region: str = "All") -> pd.Series:
    """Aggregate sales to daily frequency with optional filters."""
    filtered = df.copy()
    if category != "All":
        filtered = filtered[filtered["Category"] == category]
    if region != "All":
        filtered = filtered[filtered["Region"] == region]

    ts = (
        filtered.groupby("Order Date")[SALES_COL]
        .sum()
        .asfreq("D")
        .fillna(0)
    )
    return ts


def monthly_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly aggregated sales + profit."""
    df2 = df.copy()
    df2["Month"] = df2["Order Date"].dt.to_period("M")
    monthly = df2.groupby("Month").agg(
        Sales=(SALES_COL, "sum"),
        Profit=(PROFIT_COL, "sum"),
        Orders=("Order ID", "nunique"),
        Quantity=("Quantity", "sum"),
    ).reset_index()
    monthly["Month"] = monthly["Month"].dt.to_timestamp()
    return monthly


def kpi_summary(df: pd.DataFrame) -> dict:
    """Top-level KPI metrics."""
    total_sales  = df[SALES_COL].sum()
    total_profit = df[PROFIT_COL].sum()
    return {
        "total_sales":      total_sales,
        "total_profit":     total_profit,
        "total_orders":     df["Order ID"].nunique(),
        "profit_margin":    (total_profit / total_sales * 100) if total_sales > 0 else 0,
        "avg_order_val":    df.groupby("Order ID")[SALES_COL].sum().mean(),
        "total_customers":  df["Customer Segment"].nunique(),
        "top_state":        df.groupby("State")[SALES_COL].sum().idxmax(),
        "top_category":     df.groupby("Category")[SALES_COL].sum().idxmax(),
    }
