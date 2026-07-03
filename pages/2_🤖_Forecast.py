"""
Page 2: ML Forecast
=====================
Interactive forecasting with Prophet, XGBoost, or Ridge Regression.
Forecast runs only when the user clicks the Run Forecast button.
"""

import os
import sys
import warnings
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib

warnings.filterwarnings("ignore")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.data_loader import load_raw, daily_sales
from src.feature_engineering import make_features, FEATURE_COLS, future_frame
from src.styles import inject_css

st.set_page_config(page_title="Forecast — SalesPro AI", page_icon="🤖", layout="wide")

inject_css()
st.markdown("""
<style>
.page-title { font-size:2rem; font-weight:800; color:#E8E8F0; margin:0 0 6px 0; }
.page-desc  { font-size:0.95rem; color:#9CA3AF; margin:0; }
.model-badge {
    display:inline-block;
    background:linear-gradient(135deg,#FF6B35,#F7931E);
    border-radius:8px; padding:4px 14px;
    font-size:0.8rem; color:white; font-weight:700; margin:0 6px;
}
.forecast-stat {
    background:linear-gradient(145deg,#1A1A2E,#16213E);
    border:1px solid rgba(255,107,53,0.25);
    border-radius:12px; padding:20px; text-align:center;
}
.forecast-stat-val { font-size:1.6rem; font-weight:800; color:#FF6B35; margin:0; }
.forecast-stat-lbl { font-size:0.8rem; color:#9CA3AF; margin:4px 0 0 0;
                     text-transform:uppercase; letter-spacing:.5px; }
</style>
""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def get_data():
    return load_raw()

data_path = os.path.join(ROOT, "data", "train.csv")
if not os.path.exists(data_path):
    st.error("Dataset not found. Run `python setup.py` first.")
    st.stop()

df = get_data()

# ── Load model bundles ─────────────────────────────────────────────────────────
models_dir = os.path.join(ROOT, "models")

@st.cache_resource
def load_model(path):
    return joblib.load(path)

if not all(os.path.exists(os.path.join(models_dir, f))
           for f in ["prophet_model.pkl", "xgboost_model.pkl", "linear_model.pkl"]):
    st.error("Models not trained. Run `python setup.py` first.")
    st.stop()

# ── Sidebar controls ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🤖 Forecast Controls")
    st.divider()

    sel_model = st.radio(
        "Select Model",
        ["Prophet", "XGBoost", "Ridge Regression"],
        captions=["Best for seasonality", "Best accuracy", "Baseline model"],
    )

    st.divider()
    sel_category = st.selectbox("Filter by Category", ["All"] + sorted(df["Category"].unique().tolist()))
    sel_region   = st.selectbox("Filter by Region",   ["All"] + sorted(df["Region"].unique().tolist()))

    st.divider()
    horizon      = st.slider("Forecast Horizon (days)", min_value=7, max_value=365, value=90, step=7)
    show_history = st.slider("Show historical days",    90, 1200, 365, step=30)

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
    <h1 class="page-title">🤖 ML Sales Forecast</h1>
    <p class="page-desc">
        Model: <span class="model-badge">{sel_model}</span>
        &nbsp;|&nbsp; Horizon: <strong style="color:#FF6B35">{horizon} days</strong>
        &nbsp;|&nbsp; Filter: <strong style="color:#F7931E">{sel_category} / {sel_region}</strong>
    </p>
</div>
""", unsafe_allow_html=True)

# ── Run Forecast button ────────────────────────────────────────────────────────
col_btn, col_hint = st.columns([1, 4])
with col_btn:
    run_clicked = st.button("🚀 Run Forecast", type="primary", use_container_width=True)
with col_hint:
    st.markdown("""
    <div style="padding:14px 0; color:#9CA3AF; font-size:0.88rem;">
        Set your model, filters &amp; horizon in the sidebar,
        then click <strong style="color:#FF6B35">Run Forecast</strong> to generate predictions.
        Results are cached — changing any setting will prompt you to re-run.
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── Session state: store current params on click ───────────────────────────────
current_params = (sel_model, sel_category, sel_region, horizon, show_history)

if run_clicked:
    st.session_state["forecast_params"] = current_params

# If never clicked, or settings changed since last run → show prompt and stop
if "forecast_params" not in st.session_state:
    st.info("👆 Configure your settings in the sidebar and click **Run Forecast** to begin.")
    st.stop()

if st.session_state["forecast_params"] != current_params:
    st.warning("⚙️ Settings changed since last run — click **Run Forecast** to update the forecast.")
    st.stop()

# ── Forecast functions ─────────────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def run_prophet_forecast(horizon, category, region):
    from prophet import Prophet
    ts_local = daily_sales(load_raw(), category=category, region=region)
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode="multiplicative",
        changepoint_prior_scale=0.1,
    )
    model.fit(pd.DataFrame({"ds": ts_local.index, "y": ts_local.values}))
    future    = model.make_future_dataframe(periods=horizon)
    fc        = model.predict(future)
    fc_future = fc.tail(horizon)[["ds", "yhat", "yhat_lower", "yhat_upper"]].reset_index(drop=True)
    return fc_future, ts_local


@st.cache_data(ttl=600, show_spinner=False)
def run_xgb_forecast(horizon, category, region):
    model    = load_model(os.path.join(models_dir, "xgboost_model.pkl"))["model"]
    ts_local = daily_sales(load_raw(), category=category, region=region)
    ff       = future_frame(ts_local.index[-1], horizon, ts_local)
    preds    = np.maximum(0, model.predict(ff[FEATURE_COLS]))

    # ── Level calibration ────────────────────────────────────────────────────
    # XGBoost (tree-based) can't extrapolate, so its predicted mean may drift
    # from the actual recent level. Scale predictions to match recent 30-day
    # historical average while preserving the daily shape from calendar features.
    recent_mean = float(ts_local.iloc[-30:].mean()) if len(ts_local) >= 30 else float(ts_local.mean())
    pred_mean   = float(preds.mean())
    if pred_mean > 0 and recent_mean > 0:
        scale = np.clip(recent_mean / pred_mean, 0.5, 2.0)
        preds = preds * scale

    return pd.DataFrame({"ds": ff.index, "yhat": preds}), ts_local


@st.cache_data(ttl=600, show_spinner=False)
def run_linear_forecast(horizon, category, region):
    model    = load_model(os.path.join(models_dir, "linear_model.pkl"))["model"]
    ts_local = daily_sales(load_raw(), category=category, region=region)
    ff       = future_frame(ts_local.index[-1], horizon, ts_local)
    preds    = np.maximum(0, model.predict(ff[FEATURE_COLS]))
    return pd.DataFrame({"ds": ff.index, "yhat": preds}), ts_local


# ── Execute forecast ───────────────────────────────────────────────────────────
with st.spinner(f"Running {sel_model} forecast for {horizon} days..."):
    if sel_model == "Prophet":
        fc_df, ts_full = run_prophet_forecast(horizon, sel_category, sel_region)
        has_ci = True
    elif sel_model == "XGBoost":
        fc_df, ts_full = run_xgb_forecast(horizon, sel_category, sel_region)
        has_ci = False
    else:
        fc_df, ts_full = run_linear_forecast(horizon, sel_category, sel_region)
        has_ci = False

ts_show = ts_full.iloc[-show_history:]

# ── Guard: empty result ────────────────────────────────────────────────────────
if fc_df.empty or fc_df["yhat"].dropna().empty:
    st.warning("No forecast data returned for the selected filters. Try 'All' for Category or Region.")
    st.stop()

# ── Summary stats ──────────────────────────────────────────────────────────────
total_fc  = fc_df["yhat"].sum()
avg_daily = fc_df["yhat"].mean()
peak_idx  = fc_df["yhat"].idxmax()
peak_day  = fc_df.loc[peak_idx, "ds"]
hist_avg  = ts_full.iloc[-horizon:].mean() if len(ts_full) >= horizon else ts_full.mean()
growth    = ((avg_daily - hist_avg) / hist_avg * 100) if hist_avg != 0 else 0

col1, col2, col3, col4 = st.columns(4)
for col, val, lbl in [
    (col1, f"Rs.{total_fc:,.0f}",  f"Total Forecast ({horizon}d)"),
    (col2, f"Rs.{avg_daily:,.0f}", "Avg Daily Sales"),
    (col3, str(peak_day.date()) if hasattr(peak_day, "date") else str(peak_day), "Peak Sales Day"),
    (col4, f"{growth:+.1f}%",      "vs Prior Period"),
]:
    with col:
        st.markdown(f"""
        <div class="forecast-stat">
            <p class="forecast-stat-val">{val}</p>
            <p class="forecast-stat-lbl">{lbl}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("")

# ── Forecast chart ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📈 Historical + Forecast Chart</div>', unsafe_allow_html=True)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=ts_show.index, y=ts_show.values,
    mode="lines", name="Historical Sales",
    line=dict(color="#FF6B35", width=1.8),
    hovertemplate="<b>%{x}</b><br>Sales: Rs.%{y:,.0f}<extra></extra>",
))

if has_ci:
    fig.add_trace(go.Scatter(
        x=pd.concat([fc_df["ds"], fc_df["ds"][::-1]]),
        y=pd.concat([fc_df["yhat_upper"], fc_df["yhat_lower"][::-1]]),
        fill="toself", fillcolor="rgba(247,147,30,0.12)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=True, name="Confidence Interval", hoverinfo="skip",
    ))

fig.add_trace(go.Scatter(
    x=fc_df["ds"], y=fc_df["yhat"],
    mode="lines", name=f"{sel_model} Forecast",
    line=dict(color="#F7931E", width=2.5, dash="dot"),
    hovertemplate="<b>%{x}</b><br>Forecast: Rs.%{y:,.0f}<extra></extra>",
))

fig.add_vline(
    x=ts_show.index[-1], line_dash="dash",
    line_color="rgba(255,255,255,0.3)", line_width=1,
    annotation_text="Forecast Start",
    annotation_font_color="#9CA3AF",
    annotation_position="top right",
)

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#E8E8F0", family="Inter"),
    legend=dict(bgcolor="rgba(26,26,46,0.85)", bordercolor="rgba(255,107,53,0.3)", borderwidth=1),
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
               zeroline=False, tickprefix="Rs.", tickformat=",.0f"),
    hovermode="x unified",
    margin=dict(l=0, r=0, t=20, b=0), height=460,
)
st.plotly_chart(fig, use_container_width=True)

# ── Download ───────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">⬇️ Download Forecast</div>', unsafe_allow_html=True)

import io

dl_df = fc_df.rename(columns={"ds": "Date", "yhat": "Forecasted_Sales_INR"})
if has_ci:
    dl_df = dl_df[["Date", "Forecasted_Sales_INR", "yhat_lower", "yhat_upper"]]
    dl_df.columns = ["Date", "Forecasted_Sales_INR", "Lower_CI_INR", "Upper_CI_INR"]
dl_df["Date"] = pd.to_datetime(dl_df["Date"]).dt.strftime("%Y-%m-%d")
dl_df["Forecasted_Sales_INR"] = dl_df["Forecasted_Sales_INR"].round(2)

# Write to StringIO — avoids encoding issues that strip filename from Content-Disposition
csv_buffer = io.StringIO()
dl_df.to_csv(csv_buffer, index=False)
csv_str = csv_buffer.getvalue()

model_slug = sel_model.lower().replace(" ", "_").replace("-", "_")
fname = f"forecast_{model_slug}_{horizon}d.csv"

st.download_button(
    label=f"📥 Download {sel_model} Forecast (.csv)",
    data=csv_str,
    file_name=fname,
    mime="text/csv",
    use_container_width=False,
)

with st.expander("📋 View Forecast Data Table"):
    st.dataframe(dl_df, use_container_width=True, height=300)

