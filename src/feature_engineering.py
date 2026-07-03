"""
Feature Engineering for ML Models
====================================
Converts a daily time-series into a supervised learning DataFrame.
"""

import pandas as pd
import numpy as np


def make_features(ts: pd.Series) -> pd.DataFrame:
    """
    Given a daily sales Series (DatetimeIndex), return a feature DataFrame
    suitable for XGBoost / Linear Regression forecasting.

    Features generated:
        - Calendar: year, month, day_of_week, quarter, day_of_year, week_of_year
        - Lag features: t-1, t-7, t-14, t-30 days
        - Rolling statistics: 7-day and 30-day rolling mean & std
    """
    df = pd.DataFrame({"ds": ts.index, "y": ts.values})
    df = df.set_index("ds").sort_index()

    # ── Calendar features ──────────────────────────────────────────────────
    df["year"]         = df.index.year
    df["month"]        = df.index.month
    df["day_of_week"]  = df.index.dayofweek
    df["quarter"]      = df.index.quarter
    df["day_of_year"]  = df.index.dayofyear
    df["week_of_year"] = df.index.isocalendar().week.astype(int)
    df["is_weekend"]   = (df["day_of_week"] >= 5).astype(int)
    df["is_month_end"] = df.index.is_month_end.astype(int)
    df["is_month_start"] = df.index.is_month_start.astype(int)

    # ── Lag features ───────────────────────────────────────────────────────
    for lag in [1, 7, 14, 30]:
        df[f"lag_{lag}"] = df["y"].shift(lag)

    # ── Rolling statistics ────────────────────────────────────────────────
    df["roll_mean_7"]  = df["y"].shift(1).rolling(7).mean()
    df["roll_std_7"]   = df["y"].shift(1).rolling(7).std()
    df["roll_mean_30"] = df["y"].shift(1).rolling(30).mean()
    df["roll_std_30"]  = df["y"].shift(1).rolling(30).std()

    df.dropna(inplace=True)
    return df


FEATURE_COLS = [
    "year", "month", "day_of_week", "quarter", "day_of_year",
    "week_of_year", "is_weekend", "is_month_end", "is_month_start",
    "lag_1", "lag_7", "lag_14", "lag_30",
    "roll_mean_7", "roll_std_7", "roll_mean_30", "roll_std_30",
]


def future_frame(last_date: pd.Timestamp, horizon: int, hist_series: pd.Series) -> pd.DataFrame:
    """
    Build a future feature DataFrame for forecasting `horizon` days ahead.

    Uses DIRECT forecasting: all future rows are built from the fixed historical
    window (no recursive updates). This prevents error compounding across the
    horizon and keeps predictions consistent across models.

    Calendar features vary per day; lag/rolling features are anchored to the
    last known real values from hist_series.
    """
    future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=horizon, freq="D")

    # Pre-compute all lag/rolling anchors from real history (fixed for all future rows)
    n = len(hist_series)
    lag_1    = float(hist_series.iloc[-1])  if n >= 1  else 0.0
    lag_7    = float(hist_series.iloc[-7])  if n >= 7  else lag_1
    lag_14   = float(hist_series.iloc[-14]) if n >= 14 else lag_1
    lag_30   = float(hist_series.iloc[-30]) if n >= 30 else lag_1
    roll_m7  = float(hist_series.iloc[-7:].mean())  if n >= 7  else float(hist_series.mean())
    roll_s7  = float(hist_series.iloc[-7:].std())   if n >= 7  else 0.0
    roll_m30 = float(hist_series.iloc[-30:].mean()) if n >= 30 else float(hist_series.mean())
    roll_s30 = float(hist_series.iloc[-30:].std())  if n >= 30 else 0.0

    rows = []
    for date in future_dates:
        rows.append({
            "year":           date.year,
            "month":          date.month,
            "day_of_week":    date.dayofweek,
            "quarter":        date.quarter,
            "day_of_year":    date.dayofyear,
            "week_of_year":   date.isocalendar().week,
            "is_weekend":     int(date.dayofweek >= 5),
            "is_month_end":   int(date.is_month_end),
            "is_month_start": int(date.is_month_start),
            # All lag/rolling values fixed to last known real history
            "lag_1":          lag_1,
            "lag_7":          lag_7,
            "lag_14":         lag_14,
            "lag_30":         lag_30,
            "roll_mean_7":    roll_m7,
            "roll_std_7":     roll_s7,
            "roll_mean_30":   roll_m30,
            "roll_std_30":    roll_s30,
        })

    return pd.DataFrame(rows, index=future_dates)

