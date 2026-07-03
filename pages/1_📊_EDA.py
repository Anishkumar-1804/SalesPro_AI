"""
Page 1: Exploratory Data Analysis (EDA) — Indian E-Commerce
=============================================================
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from src.data_loader import load_raw
from src.styles import inject_css

st.set_page_config(page_title="EDA — SalesPro AI", page_icon="📊", layout="wide")

inject_css()
st.markdown("""
<style>
.page-header {
    background: linear-gradient(135deg, #1A1A2E, #16213E);
    border: 1px solid rgba(255,107,53,0.3);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 28px;
}
.page-title { font-size:2rem; font-weight:800; color:#E8E8F0; margin:0 0 6px 0; }
.page-desc  { font-size:0.95rem; color:#9CA3AF; margin:0; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def get_data():
    return load_raw()

data_path = os.path.join(ROOT, "data", "train.csv")
if not os.path.exists(data_path):
    st.error("Dataset not found. Run `python setup.py` first.")
    st.stop()

df = get_data()
SALES_COL  = "Sales (INR)"
PROFIT_COL = "Profit (INR)"

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 EDA Filters")
    st.divider()
    sel_cats = st.multiselect("Category",  df["Category"].unique().tolist(),
                               default=df["Category"].unique().tolist())
    sel_regs = st.multiselect("Region",    df["Region"].unique().tolist(),
                               default=df["Region"].unique().tolist())
    sel_segs = st.multiselect("Segment",   df["Customer Segment"].unique().tolist(),
                               default=df["Customer Segment"].unique().tolist())
    agg_level = st.selectbox("Time Aggregation", ["Monthly", "Weekly", "Quarterly", "Yearly"])

agg_map = {"Monthly": "M", "Weekly": "W", "Quarterly": "Q", "Yearly": "Y"}

filtered = df[
    df["Category"].isin(sel_cats) &
    df["Region"].isin(sel_regs) &
    df["Customer Segment"].isin(sel_segs)
].copy()

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1 class="page-title">📊 Exploratory Data Analysis — India</h1>
    <p class="page-desc">
        Deep-dive into Indian e-commerce sales data — trends, categories,
        states, festival patterns, and more.
    </p>
</div>
""", unsafe_allow_html=True)
st.markdown(f"**Showing {len(filtered):,} of {len(df):,} delivered/shipped records**")

# ─────────────────────────────────────────────────────────────────────────────
# 1. Sales Trend
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📅 Sales Trend Over Time (INR)</div>', unsafe_allow_html=True)

freq = agg_map[agg_level]
ts_data = (
    filtered.set_index("Order Date")[SALES_COL]
    .resample(freq).sum().reset_index()
)
ts_data.columns = ["Date", "Sales"]

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=ts_data["Date"], y=ts_data["Sales"],
    mode="lines+markers",
    fill="tozeroy",
    fillcolor="rgba(255,107,53,0.10)",
    line=dict(color="#FF6B35", width=2.5),
    marker=dict(size=5, color="#FF6B35"),
    hovertemplate="<b>%{x}</b><br>Sales: Rs.%{y:,.0f}<extra></extra>",
))
fig_trend.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#E8E8F0", family="Inter"),
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
               zeroline=False, tickprefix="Rs.", tickformat=",.0f"),
    hovermode="x unified",
    margin=dict(l=0, r=0, t=10, b=0), height=340,
)
st.plotly_chart(fig_trend, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# 2. Sub-Category & Segment
# ─────────────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">🗂️ Sales by Sub-Category</div>', unsafe_allow_html=True)
    sub_sales = (
        filtered.groupby("Sub-Category")[SALES_COL].sum()
        .sort_values(ascending=True).reset_index()
    )
    fig_sub = px.bar(
        sub_sales, x=SALES_COL, y="Sub-Category", orientation="h",
        color=SALES_COL,
        color_continuous_scale=[[0,"#4A1500"],[0.5,"#FF6B35"],[1,"#FFB347"]],
    )
    fig_sub.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E8E8F0", family="Inter"), coloraxis_showscale=False,
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                   tickprefix="Rs.", tickformat=",.0f"),
        yaxis=dict(showgrid=False, tickfont=dict(size=10)),
        margin=dict(l=0, r=0, t=10, b=0), height=480,
    )
    st.plotly_chart(fig_sub, use_container_width=True)

with col2:
    st.markdown('<div class="section-header">👥 Sales by Customer Segment</div>', unsafe_allow_html=True)
    seg_sales = filtered.groupby("Customer Segment")[SALES_COL].sum().reset_index()
    fig_seg = px.pie(
        seg_sales, names="Customer Segment", values=SALES_COL,
        color_discrete_sequence=["#FF6B35","#F7931E","#FFB347","#FF4500"],
        hole=0.5,
    )
    fig_seg.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E8E8F0", family="Inter"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=0, r=0, t=10, b=0), height=240,
    )
    fig_seg.update_traces(textfont_color="white")
    st.plotly_chart(fig_seg, use_container_width=True)

    st.markdown('<div class="section-header">🚚 Sales by Fulfilment Type</div>', unsafe_allow_html=True)
    ful_sales = (
        filtered.groupby("Fulfilment")[SALES_COL].sum()
        .sort_values(ascending=False).reset_index()
    )
    fig_ful = px.bar(
        ful_sales, x="Fulfilment", y=SALES_COL,
        color_discrete_sequence=["#FF6B35"],
    )
    fig_ful.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E8E8F0", family="Inter"),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                   tickprefix="Rs.", tickformat=",.0f"),
        margin=dict(l=0, r=0, t=10, b=0), height=200,
    )
    st.plotly_chart(fig_ful, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# 3. Profit vs Sales scatter
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">💹 Profit vs Sales (INR) by Category</div>', unsafe_allow_html=True)

fig_scatter = px.scatter(
    filtered, x=SALES_COL, y=PROFIT_COL,
    color="Category", size="Quantity", opacity=0.6,
    color_discrete_sequence=["#FF6B35","#F7931E","#FFB347","#FF4500","#FFA07A","#FF7F50"],
    hover_data=["Sub-Category", "Region", "State", "City", "Payment Mode"],
)
fig_scatter.add_hline(y=0, line_dash="dash", line_color="rgba(255,80,80,0.5)", line_width=1)
fig_scatter.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#E8E8F0", family="Inter"),
    legend=dict(bgcolor="rgba(26,26,46,0.8)", bordercolor="rgba(255,107,53,0.3)", borderwidth=1),
    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
               zeroline=False, tickprefix="Rs.", tickformat=",.0f"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
               zeroline=False, tickprefix="Rs.", tickformat=",.0f"),
    margin=dict(l=0, r=0, t=10, b=0), height=400,
)
st.plotly_chart(fig_scatter, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# 4. Festival Sales Heatmap — Month × Year
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🪔 Monthly Sales Heatmap — Festival Peaks Visible</div>', unsafe_allow_html=True)

heat_df = filtered.copy()
heat_df["Year"]  = heat_df["Order Date"].dt.year
heat_df["Month"] = heat_df["Order Date"].dt.strftime("%b")
heat_pivot = heat_df.groupby(["Year", "Month"])[SALES_COL].sum().unstack()

month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
heat_pivot = heat_pivot.reindex(columns=[m for m in month_order if m in heat_pivot.columns])

fig_heat = go.Figure(data=go.Heatmap(
    z=heat_pivot.values,
    x=heat_pivot.columns.tolist(),
    y=[str(y) for y in heat_pivot.index.tolist()],
    colorscale=[[0,"#0F0F1A"],[0.3,"#4A1500"],[0.7,"#FF6B35"],[1,"#FFD700"]],
    hovertemplate="<b>%{y} — %{x}</b><br>Sales: Rs.%{z:,.0f}<extra></extra>",
    text=[[f"Rs.{v/1e5:.1f}L" for v in row] for row in heat_pivot.values],
    texttemplate="%{text}",
    textfont=dict(size=10, color="white"),
))
fig_heat.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#E8E8F0", family="Inter"),
    xaxis=dict(side="top"),
    margin=dict(l=0, r=0, t=10, b=0), height=230,
    annotations=[dict(
        text="Oct-Nov peaks = Navratri / Diwali | Mar = Holi | Aug = Independence Day Sale",
        x=0.5, y=-0.12, xref="paper", yref="paper",
        showarrow=False, font=dict(size=10, color="#9CA3AF"),
    )],
)
st.plotly_chart(fig_heat, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# 5. Top States Sales
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🏆 Top 15 Indian States by Sales</div>', unsafe_allow_html=True)

state_sales = (
    filtered.groupby("State")[SALES_COL].sum()
    .nlargest(15).sort_values(ascending=True).reset_index()
)
fig_state = px.bar(
    state_sales, x=SALES_COL, y="State", orientation="h",
    color=SALES_COL,
    color_continuous_scale=[[0,"#4A1500"],[0.5,"#FF6B35"],[1,"#FFB347"]],
)
fig_state.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#E8E8F0", family="Inter"), coloraxis_showscale=False,
    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
               tickprefix="Rs.", tickformat=",.0f"),
    yaxis=dict(showgrid=False, tickfont=dict(size=11)),
    margin=dict(l=0, r=0, t=10, b=0), height=420,
)
st.plotly_chart(fig_state, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# 6. Discount impact
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🏷️ Discount Impact on Sales & Profit (INR)</div>', unsafe_allow_html=True)

disc_df = (
    filtered.groupby("Discount")[[SALES_COL, PROFIT_COL]].mean().reset_index()
)
fig_disc = go.Figure()
fig_disc.add_trace(go.Bar(
    x=(disc_df["Discount"] * 100).astype(int).astype(str) + "%",
    y=disc_df[SALES_COL],
    name="Avg Sales", marker_color="rgba(255,107,53,0.75)",
    hovertemplate="Discount %{x}<br>Avg Sales: Rs.%{y:,.0f}<extra></extra>",
))
fig_disc.add_trace(go.Bar(
    x=(disc_df["Discount"] * 100).astype(int).astype(str) + "%",
    y=disc_df[PROFIT_COL],
    name="Avg Profit", marker_color="rgba(247,147,30,0.75)",
    hovertemplate="Discount %{x}<br>Avg Profit: Rs.%{y:,.0f}<extra></extra>",
))
fig_disc.update_layout(
    barmode="group",
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#E8E8F0", family="Inter"),
    legend=dict(bgcolor="rgba(26,26,46,0.8)", bordercolor="rgba(255,107,53,0.3)", borderwidth=1),
    xaxis=dict(showgrid=False, title="Discount Rate"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
               tickprefix="Rs.", tickformat=",.0f"),
    margin=dict(l=0, r=0, t=10, b=0), height=320,
)
st.plotly_chart(fig_disc, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# 7. GST Collection by Category
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📋 GST Collection by Category (INR)</div>', unsafe_allow_html=True)

gst_df = filtered.groupby("Category")["GST (INR)"].sum().sort_values(ascending=False).reset_index()
fig_gst = px.bar(
    gst_df, x="Category", y="GST (INR)",
    color="GST (INR)",
    color_continuous_scale=[[0,"#1A0800"],[0.5,"#FF6B35"],[1,"#FFD700"]],
)
fig_gst.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#E8E8F0", family="Inter"), coloraxis_showscale=False,
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
               tickprefix="Rs.", tickformat=",.0f"),
    margin=dict(l=0, r=0, t=10, b=0), height=300,
)
st.plotly_chart(fig_gst, use_container_width=True)
