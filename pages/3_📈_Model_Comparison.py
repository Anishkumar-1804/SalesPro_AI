"""
Page 3: Model Comparison
==========================
Side-by-side evaluation of all three models.
"""

import os
import sys
import warnings
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import joblib

warnings.filterwarnings("ignore")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.data_loader import load_raw, daily_sales
from src.feature_engineering import make_features, FEATURE_COLS
from src.evaluate import evaluate_all
from src.styles import inject_css

st.set_page_config(page_title="Model Comparison — SalesPro AI", page_icon="📈", layout="wide")

inject_css()
st.markdown("""
<style>
.best-model-card {
    background: linear-gradient(135deg, rgba(255,107,53,0.15), rgba(247,147,30,0.1));
    border: 2px solid rgba(255,107,53,0.45);
    border-radius: 16px;
    padding: 24px 32px;
    text-align: center;
    margin-bottom: 24px;
}
.best-model-name { font-size:1.8rem; font-weight:800; color:#FF6B35; margin:4px 0; }
.best-model-lbl  { font-size:0.85rem; color:#9CA3AF; margin:0;
                   text-transform:uppercase; letter-spacing:1px; }
</style>
""", unsafe_allow_html=True)

# ── Load everything ───────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def get_data():
    return load_raw()

data_path = os.path.join(ROOT, "data", "train.csv")
models_dir = os.path.join(ROOT, "models")

if not os.path.exists(data_path):
    st.error("Dataset not found. Run `python setup.py` first.")
    st.stop()

model_files = {
    "Prophet":         "prophet_model.pkl",
    "XGBoost":         "xgboost_model.pkl",
    "Ridge Regression":"linear_model.pkl",
}
if not all(os.path.exists(os.path.join(models_dir, f)) for f in model_files.values()):
    st.error("Models not trained. Run `python setup.py` first.")
    st.stop()

df = get_data()

@st.cache_resource
def load_model(path):
    return joblib.load(path)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📈 Comparison Settings")
    st.divider()
    test_days = st.slider("Test window (days)", 30, 180, 90, step=15)
    sel_cat   = st.selectbox("Category", ["All"] + sorted(df["Category"].unique().tolist()))
    sel_reg   = st.selectbox("Region",   ["All"] + sorted(df["Region"].unique().tolist()))

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1 class="page-title">📈 Model Comparison</h1>
    <p class="page-desc">Evaluate Prophet, XGBoost, and Ridge Regression side-by-side using held-out test data.</p>
</div>
""", unsafe_allow_html=True)

# ── Evaluate models on test set ────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=True)
def evaluate_models(test_days, category, region):
    from prophet import Prophet
    ts = daily_sales(load_raw(), category=category, region=region)
    ts_train = ts.iloc[:-test_days]
    ts_test  = ts.iloc[-test_days:]
    results = {}

    # ── Prophet — always instantiate fresh (saved model cannot be re-fit) ──
    prophet_model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode="multiplicative",
        changepoint_prior_scale=0.1,
    )
    train_df = pd.DataFrame({"ds": ts_train.index, "y": ts_train.values})
    prophet_model.fit(train_df)
    future = prophet_model.make_future_dataframe(periods=test_days)
    fc = prophet_model.predict(future)
    y_pred_prophet = fc.iloc[-test_days:]["yhat"].values
    results["Prophet"] = {
        "metrics": evaluate_all(ts_test.values, y_pred_prophet),
        "y_true": ts_test.values,
        "y_pred": y_pred_prophet,
        "dates":  ts_test.index,
    }

    # ── XGBoost ──
    bundle_xgb = load_model(os.path.join(models_dir, "xgboost_model.pkl"))
    xgb_model = bundle_xgb["model"]
    feat_df = make_features(ts_train)
    X_test_feat = make_features(ts)
    X_test_feat = X_test_feat[X_test_feat.index >= ts_test.index[0]]
    X_test_final = X_test_feat[FEATURE_COLS].iloc[:test_days]
    y_pred_xgb = xgb_model.predict(X_test_final)
    y_true_xgb = ts_test.values[:len(y_pred_xgb)]
    results["XGBoost"] = {
        "metrics": evaluate_all(y_true_xgb, y_pred_xgb),
        "y_true": y_true_xgb,
        "y_pred": y_pred_xgb,
        "dates":  ts_test.index[:len(y_pred_xgb)],
    }

    # ── Linear ──
    bundle_lin = load_model(os.path.join(models_dir, "linear_model.pkl"))
    lin_model = bundle_lin["model"]
    y_pred_lin = lin_model.predict(X_test_final)
    results["Ridge Regression"] = {
        "metrics": evaluate_all(y_true_xgb, y_pred_lin),
        "y_true": y_true_xgb,
        "y_pred": y_pred_lin,
        "dates":  ts_test.index[:len(y_pred_lin)],
    }

    return results

with st.spinner("Evaluating models on test data …"):
    results = evaluate_models(test_days, sel_cat, sel_reg)

# ── Best model ─────────────────────────────────────────────────────────────────
best_model = min(results, key=lambda k: results[k]["metrics"]["RMSE"])

st.markdown(f"""
<div class="best-model-card">
    <p class="best-model-lbl">🏆 Best Model (by RMSE)</p>
    <p class="best-model-name">{best_model}</p>
    <p style="color:#9CA3AF;font-size:0.85rem;margin:4px 0 0 0;">
        RMSE: <strong style="color:#06B6D4">Rs.{results[best_model]['metrics']['RMSE']:,.2f}</strong>
        &nbsp;|&nbsp;
        MAE: <strong style="color:#06B6D4">Rs.{results[best_model]['metrics']['MAE']:,.2f}</strong>
        &nbsp;|&nbsp;
        MAPE: <strong style="color:#06B6D4">{results[best_model]['metrics']['MAPE']:.2f}%</strong>
        &nbsp;|&nbsp;
        R2: <strong style="color:#06B6D4">{results[best_model]['metrics']['R2']:.4f}</strong>
    </p>
</div>
""", unsafe_allow_html=True)

# ── Metrics table ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📊 Performance Metrics Comparison</div>', unsafe_allow_html=True)

rows = []
for name, data in results.items():
    m = data["metrics"]
    rows.append({
        "Model": name,
        "MAE (Rs.)": m["MAE"],
        "RMSE (Rs.)": m["RMSE"],
        "MAPE (%)": m["MAPE"],
        "R2":        m["R2"],
        "Best":     "Best" if name == best_model else "",
    })
metrics_df = pd.DataFrame(rows).set_index("Model")

def highlight_best(row):
    styles = []
    for col in row.index:
        if col == "Best":
            styles.append("color: #FFD700; font-weight: bold;")
        elif row.name == best_model:
            styles.append("background-color: rgba(108,99,255,0.15); color: #E8E8F0;")
        else:
            styles.append("color: #9CA3AF;")
    return styles

st.dataframe(
    metrics_df.style.apply(highlight_best, axis=1).format({
        "MAE (Rs.)": "{:,.2f}", "RMSE (Rs.)": "{:,.2f}",
        "MAPE (%)": "{:.2f}", "R2": "{:.4f}",
    }),
    use_container_width=True,
    height=160,
)

# ── Download buttons ───────────────────────────────────────────────────────────
import io
dl_col1, dl_col2 = st.columns(2)

with dl_col1:
    # Metrics summary CSV
    metrics_buffer = io.StringIO()
    metrics_df.reset_index().to_csv(metrics_buffer, index=False)
    metrics_str = metrics_buffer.getvalue()
    
    st.download_button(
        label="📥 Download Metrics Summary (.csv)",
        data=metrics_str,
        file_name="model_comparison_metrics.csv",
        mime="text/csv",
        use_container_width=True,
    )

with dl_col2:
    # Full actual vs predicted CSV for all models
    pred_frames = []
    for name, data in results.items():
        frame = pd.DataFrame({
            "Date":          data["dates"],
            "Actual_Sales_INR": data["y_true"],
            f"{name}_Predicted_INR": data["y_pred"],
        }).set_index("Date")
        pred_frames.append(frame)

    combined = pred_frames[0]
    for f in pred_frames[1:]:
        combined = combined.join(f.drop(columns=["Actual_Sales_INR"], errors="ignore"), how="outer")
    combined = combined.reset_index()

    preds_buffer = io.StringIO()
    combined.to_csv(preds_buffer, index=False)
    preds_str = preds_buffer.getvalue()

    st.download_button(
        label="📥 Download Actual vs Predicted (.csv)",
        data=preds_str,
        file_name="model_comparison_predictions.csv",
        mime="text/csv",
        use_container_width=True,
    )

# ── Grouped bar chart ──────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Metrics Bar Chart</div>', unsafe_allow_html=True)

metric_names  = ["MAE", "RMSE", "MAPE", "R2"]
metric_keys   = ["MAE ($)", "RMSE ($)", "MAPE (%)", "R2"]
model_names   = list(results.keys())
model_colors  = ["#6C63FF", "#06B6D4", "#10B981"]

fig_bar = go.Figure()
for idx, (name, color) in enumerate(zip(model_names, model_colors)):
    m = results[name]["metrics"]
    fig_bar.add_trace(go.Bar(
        name=name,
        x=["MAE ($)", "RMSE ($)", "MAPE (%)", "R²"],
        y=[m["MAE"], m["RMSE"], m["MAPE"], m["R2"]],
        marker_color=color,
        marker_opacity=0.8,
        hovertemplate="<b>%{x}</b><br>" + name + ": %{y:.2f}<extra></extra>",
    ))

fig_bar.update_layout(
    barmode="group",
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#E8E8F0", family="Inter"),
    legend=dict(bgcolor="rgba(26,26,46,0.8)", bordercolor="rgba(108,99,255,0.3)", borderwidth=1),
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False),
    margin=dict(l=0, r=0, t=20, b=0), height=340,
)
st.plotly_chart(fig_bar, use_container_width=True)

# ── Actual vs Predicted charts ─────────────────────────────────────────────────
st.markdown('<div class="section-header">📈 Actual vs Predicted — All Models</div>', unsafe_allow_html=True)

colors_map = {"Prophet": "#6C63FF", "XGBoost": "#06B6D4", "Ridge Regression": "#10B981"}
fig_avp = go.Figure()

# Plot actual once (use Prophet dates as reference)
ref_dates = results["Prophet"]["dates"]
ref_true  = results["Prophet"]["y_true"]
fig_avp.add_trace(go.Scatter(
    x=ref_dates, y=ref_true,
    mode="lines",
    name="Actual Sales",
    line=dict(color="#E8E8F0", width=2),
    hovertemplate="<b>%{x}</b><br>Actual: Rs.%{y:,.0f}<extra></extra>",
))

for name, data in results.items():
    color = colors_map[name]
    fig_avp.add_trace(go.Scatter(
        x=data["dates"], y=data["y_pred"],
        mode="lines",
        name=f"{name} Prediction",
        line=dict(color=color, width=1.8, dash="dot"),
        hovertemplate=f"<b>%{{x}}</b><br>{name}: Rs.%{{y:,.0f}}<extra></extra>",
    ))

fig_avp.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#E8E8F0", family="Inter"),
    legend=dict(bgcolor="rgba(26,26,46,0.85)", bordercolor="rgba(108,99,255,0.3)", borderwidth=1),
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
               zeroline=False, tickprefix="Rs.", tickformat=",.0f"),
    hovermode="x unified",
    margin=dict(l=0, r=0, t=20, b=0), height=460,
)
st.plotly_chart(fig_avp, use_container_width=True)

# ── Residual error distribution ────────────────────────────────────────────────
st.markdown('<div class="section-header">🔍 Residual Error Distribution</div>', unsafe_allow_html=True)

fig_res = go.Figure()
for name, data in results.items():
    residuals = np.array(data["y_true"]) - np.array(data["y_pred"])
    fig_res.add_trace(go.Histogram(
        x=residuals, name=name, opacity=0.65,
        nbinsx=40, marker_color=colors_map[name],
        hovertemplate=f"{name}<br>Residual: %{{x:,.0f}}<extra></extra>",
    ))

fig_res.add_vline(x=0, line_dash="dash", line_color="rgba(255,255,255,0.4)", line_width=1.5)
fig_res.update_layout(
    barmode="overlay",
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#E8E8F0", family="Inter"),
    legend=dict(bgcolor="rgba(26,26,46,0.8)", bordercolor="rgba(108,99,255,0.3)", borderwidth=1),
    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
               zeroline=False, title="Residual (Actual − Predicted)"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title="Count"),
    margin=dict(l=0, r=0, t=20, b=0), height=320,
)
st.plotly_chart(fig_res, use_container_width=True)

# ── Model info cards ───────────────────────────────────────────────────────────
st.markdown('<div class="section-header">ℹ️ Model Details</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

with c1:
    st.info("""
**🔮 Prophet**
Meta's open-source time series model.
Captures yearly & weekly seasonality automatically.
Robust to missing data and outliers.
Best for: trend + seasonality dominant datasets.
    """)
with c2:
    st.info("""
**⚡ XGBoost**
Gradient Boosted Trees with engineered lag/calendar features.
Treats forecasting as a supervised regression problem.
Highly accurate for structured tabular data.
Best for: complex nonlinear patterns.
    """)
with c3:
    st.info("""
**📐 Ridge Regression**
Regularized Linear Regression (L2 penalty).
Uses same feature set as XGBoost.
Interpretable and fast to train.
Best for: linear trend baselines.
    """)
