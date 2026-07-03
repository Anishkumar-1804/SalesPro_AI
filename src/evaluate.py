"""
Evaluation Metrics
==================
Common regression metrics for time-series model evaluation.
"""

import numpy as np
import pandas as pd


def mae(y_true, y_pred) -> float:
    """Mean Absolute Error."""
    return float(np.mean(np.abs(np.array(y_true) - np.array(y_pred))))


def rmse(y_true, y_pred) -> float:
    """Root Mean Squared Error."""
    return float(np.sqrt(np.mean((np.array(y_true) - np.array(y_pred)) ** 2)))


def mape(y_true, y_pred) -> float:
    """Mean Absolute Percentage Error (avoids division by zero)."""
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    mask = y_true != 0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def r2(y_true, y_pred) -> float:
    """R-squared score."""
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1 - ss_res / ss_tot) if ss_tot != 0 else 0.0


def evaluate_all(y_true, y_pred) -> dict:
    """Return all metrics as a dict."""
    return {
        "MAE":  round(mae(y_true, y_pred), 2),
        "RMSE": round(rmse(y_true, y_pred), 2),
        "MAPE": round(mape(y_true, y_pred), 2),
        "R2":   round(r2(y_true, y_pred), 4),
    }
