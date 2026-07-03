"""
Sales Forecasting System — Home Page (SalesPro AI)
==========================================================
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from src.data_loader import load_raw, monthly_sales, kpi_summary
from src.styles import inject_css

st.set_page_config(
    page_title="SalesPro AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
st.markdown("""
<style>
.hero-banner {
    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 40%, #FF4500 100%);
    border-radius: 20px;
    padding: 48px 40px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -40%; right: -8%;
    width: 420px; height: 420px;
    background: rgba(255,255,255,0.06);
    border-radius: 50%;
}
.hero-banner::after {
    content: '';
    position: absolute;
    bottom: -50%; right: 15%;
    width: 280px; height: 280px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
}
.hero-title   { font-size:2.8rem; font-weight:800; color:white; margin:0 0 8px 0; line-height:1.2; }
.hero-subtitle{ font-size:1.05rem; color:rgba(255,255,255,0.88); margin:0; }
.hero-badge   {
    display:inline-block; background:rgba(255,255,255,0.2);
    backdrop-filter:blur(10px); border:1px solid rgba(255,255,255,0.3);
    border-radius:50px; padding:6px 16px; font-size:0.8rem;
    color:white; margin-bottom:16px; font-weight:700; letter-spacing:.5px;
}
.kpi-card {
    background: linear-gradient(145deg, #1A1A2E, #16213E);
    border: 1px solid rgba(255,107,53,0.25);
    border-radius: 16px;
    padding: 24px 16px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.kpi-card::after {
    content:''; position:absolute; top:0; left:0; right:0;
    height:3px;
    background:linear-gradient(90deg, #FF6B35, #F7931E);
    border-radius:16px 16px 0 0;
}
.kpi-value { font-size:1.7rem; font-weight:800; color:#FF6B35; margin:0; }
.kpi-label { font-size:0.78rem; color:#9CA3AF; margin:6px 0 0 0;
             font-weight:500; text-transform:uppercase; letter-spacing:.5px; }
.kpi-icon  { font-size:1.4rem; margin-bottom:4px; }
.source-box {
    background: linear-gradient(135deg, rgba(247,147,30,0.08), rgba(255,107,53,0.08));
    border: 1px solid rgba(247,147,30,0.3);
    border-radius: 12px;
    padding: 20px 24px;
    margin: 16px 0;
}
.source-title { font-size:.85rem; font-weight:700; color:#F7931E;
                margin:0 0 10px 0; text-transform:uppercase; letter-spacing:1px; }
.source-text  { font-size:.87rem; color:#9CA3AF; line-height:1.7; margin:0; }
.source-link  { color:#FF6B35; text-decoration:none; font-weight:600; }

.sidebar-logo { font-size:1.3rem; font-weight:800; color:#FF6B35; padding:12px 0; }
</style>
""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def get_data():
    return load_raw()

data_path = os.path.join(ROOT, "data", "train.csv")
if not os.path.exists(data_path):
    st.error("Dataset not found. Please run `python setup.py` first.")
    st.stop()

df = get_data()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">SalesPro AI</div>', unsafe_allow_html=True)
    st.divider()

    st.markdown("**🗓️ Date Range Filter**")
    min_date = df["Order Date"].min().date()
    max_date = df["Order Date"].max().date()
    date_from = st.date_input("From", value=min_date, min_value=min_date, max_value=max_date)
    date_to   = st.date_input("To",   value=max_date, min_value=min_date, max_value=max_date)

    st.divider()
    st.markdown("**🔍 Filters**")
    sel_category = st.selectbox("Category", ["All"] + sorted(df["Category"].unique().tolist()))
    sel_region   = st.selectbox("Region",   ["All"] + sorted(df["Region"].unique().tolist()))

    st.divider()
    st.markdown("""
    <div style="font-size:0.75rem;color:#6B7280;">
    Use the sidebar pages to explore EDA, Forecasting, and Model Comparison.
    </div>
    """, unsafe_allow_html=True)

# ── Filter data ────────────────────────────────────────────────────────────────
filtered = df[
    (df["Order Date"].dt.date >= date_from) &
    (df["Order Date"].dt.date <= date_to)
]
if sel_category != "All":
    filtered = filtered[filtered["Category"] == sel_category]
if sel_region != "All":
    filtered = filtered[filtered["Region"] == sel_region]

# ── Hero Banner ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-badge">🤖 Machine Learning &nbsp;|&nbsp; Indian E-Commerce Analytics</div>
    <h1 class="hero-title">SalesPro AI</h1>
    <p class="hero-subtitle">
        Powered by Prophet · XGBoost · Ridge Regression<br/>
        Forecasting across India — from Kashmir to Kanyakumari.
        Festival-aware seasonality &nbsp;|&nbsp; INR pricing &nbsp;|&nbsp; GST-inclusive reporting.
    </p>
</div>

""", unsafe_allow_html=True)

# ── KPI Cards ──────────────────────────────────────────────────────────────────
kpis = kpi_summary(filtered)

col1, col2, col3, col4, col5, col6 = st.columns(6)
kpi_data = [
    (col1, f"Rs.{kpis['total_sales']/1e7:.2f} Cr",   "Total Sales",        "📦"),
    (col2, f"Rs.{kpis['total_profit']/1e5:.1f} L",   "Total Profit",       "💰"),
    (col3, f"{kpis['total_orders']:,}",                "Total Orders",       "🛒"),
    (col4, f"{kpis['profit_margin']:.1f}%",           "Profit Margin",      "📊"),
    (col5, f"Rs.{kpis['avg_order_val']:,.0f}",        "Avg Order Value",    "🎯"),
    (col6, kpis["top_state"],                          "Top State",          "🏆"),
]
for col, value, label, icon in kpi_data:
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">{icon}</div>
            <p class="kpi-value">{value}</p>
            <p class="kpi-label">{label}</p>
        </div>
        """, unsafe_allow_html=True)

# ── Monthly Trend ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📅 Monthly Sales & Profit Trend (INR)</div>', unsafe_allow_html=True)

monthly = monthly_sales(filtered)

fig = go.Figure()
fig.add_trace(go.Bar(
    x=monthly["Month"], y=monthly["Sales"],
    name="Sales (INR)",
    marker_color="rgba(255,107,53,0.75)",
    hovertemplate="<b>%{x|%b %Y}</b><br>Sales: Rs.%{y:,.0f}<extra></extra>",
))
fig.add_trace(go.Scatter(
    x=monthly["Month"], y=monthly["Profit"],
    name="Profit (INR)", mode="lines+markers",
    line=dict(color="#F7931E", width=2.5),
    marker=dict(size=6, color="#F7931E"),
    hovertemplate="<b>%{x|%b %Y}</b><br>Profit: Rs.%{y:,.0f}<extra></extra>",
))

# Mark Diwali months
diwali_months = monthly[monthly["Month"].dt.month == 11]
if not diwali_months.empty:
    for _, row in diwali_months.iterrows():
        fig.add_vline(
            x=row["Month"], line_dash="dot",
            line_color="rgba(255,215,0,0.4)", line_width=1.5,
        )

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#E8E8F0", family="Inter"),
    legend=dict(bgcolor="rgba(26,26,46,0.8)", bordercolor="rgba(255,107,53,0.3)", borderwidth=1),
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False,
               tickprefix="Rs.", tickformat=",.0f"),
    hovermode="x unified",
    annotations=[dict(
        x=0.01, y=0.97, xref="paper", yref="paper",
        text="Gold lines = Diwali months (Nov)",
        showarrow=False, font=dict(size=10, color="#9CA3AF"),
    )],
    margin=dict(l=0, r=0, t=20, b=0), height=380,
)
st.plotly_chart(fig, use_container_width=True)

# ── Two column charts ──────────────────────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.markdown('<div class="section-header">🗂️ Sales by Category</div>', unsafe_allow_html=True)
    cat_sales = filtered.groupby("Category")["Sales (INR)"].sum().reset_index()
    fig_cat = px.pie(
        cat_sales, names="Category", values="Sales (INR)",
        color_discrete_sequence=["#FF6B35","#F7931E","#FFB347","#FF4500","#FFA07A","#FF7F50"],
        hole=0.55,
    )
    fig_cat.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E8E8F0", family="Inter"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        margin=dict(l=0, r=0, t=10, b=0), height=320,
    )
    fig_cat.update_traces(textfont_color="white")
    st.plotly_chart(fig_cat, use_container_width=True)

with col_b:
    st.markdown('<div class="section-header">🌍 Sales by Region</div>', unsafe_allow_html=True)
    reg_sales = (
        filtered.groupby("Region")["Sales (INR)"].sum()
        .reset_index().sort_values("Sales (INR)", ascending=True)
    )
    fig_reg = px.bar(
        reg_sales, x="Sales (INR)", y="Region", orientation="h",
        color="Sales (INR)",
        color_continuous_scale=[[0,"#4A1500"],[0.5,"#FF6B35"],[1,"#F7931E"]],
    )
    fig_reg.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E8E8F0", family="Inter"),
        coloraxis_showscale=False,
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                   tickprefix="Rs.", tickformat=",.0f"),
        yaxis=dict(showgrid=False),
        margin=dict(l=0, r=0, t=10, b=0), height=320,
    )
    st.plotly_chart(fig_reg, use_container_width=True)

# ── Top States ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🏆 Top 10 States by Sales</div>', unsafe_allow_html=True)
state_sales = (
    filtered.groupby("State")["Sales (INR)"].sum()
    .nlargest(10).sort_values(ascending=True).reset_index()
)
fig_st = px.bar(
    state_sales, x="Sales (INR)", y="State", orientation="h",
    color="Sales (INR)",
    color_continuous_scale=[[0,"#4A1500"],[0.5,"#FF6B35"],[1,"#FFB347"]],
)
fig_st.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#E8E8F0", family="Inter"), coloraxis_showscale=False,
    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
               tickprefix="Rs.", tickformat=",.0f"),
    yaxis=dict(showgrid=False),
    margin=dict(l=0, r=0, t=10, b=0), height=340,
)
st.plotly_chart(fig_st, use_container_width=True)

# ── Payment Mode & Festival info ───────────────────────────────────────────────
col_p, col_f = st.columns(2)

with col_p:
    st.markdown('<div class="section-header">💳 Payment Mode Split</div>', unsafe_allow_html=True)
    pay_sales = filtered.groupby("Payment Mode")["Sales (INR)"].sum().reset_index()
    fig_pay = px.bar(
        pay_sales.sort_values("Sales (INR)", ascending=False),
        x="Payment Mode", y="Sales (INR)",
        color="Payment Mode",
        color_discrete_sequence=["#FF6B35","#F7931E","#FFB347","#FF4500","#FFA07A","#FF7F50"],
    )
    fig_pay.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E8E8F0", family="Inter"),
        showlegend=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                   tickprefix="Rs.", tickformat=",.0f"),
        margin=dict(l=0, r=0, t=10, b=0), height=280,
    )
    st.plotly_chart(fig_pay, use_container_width=True)

with col_f:
    st.markdown('<div class="section-header">🪔 Indian Festival Seasonality</div>', unsafe_allow_html=True)
    festival_data = {
        "Month": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "Boost": [0.82,0.76,0.95,0.80,0.85,0.78,0.82,1.05,1.15,1.55,1.65,1.20],
        "Festival": [
            "Republic Day","—","Holi","—","Summer Sale","—",
            "—","Independence Day","Navratri/Onam","Navratri+Dussehra",
            "Diwali (Peak)","Christmas/Year-End"
        ]
    }
    fest_df = pd.DataFrame(festival_data)
    fig_fest = px.bar(
        fest_df, x="Month", y="Boost",
        color="Boost",
        color_continuous_scale=[[0,"#1A0800"],[0.5,"#FF6B35"],[1,"#FFD700"]],
        hover_data=["Festival"],
    )
    fig_fest.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E8E8F0", family="Inter"),
        coloraxis_showscale=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title="Sales Multiplier"),
        margin=dict(l=0, r=0, t=10, b=0), height=280,
    )
    st.plotly_chart(fig_fest, use_container_width=True)

# ── Dataset Source ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📌 Dataset Information</div>', unsafe_allow_html=True)

st.markdown("""
<div class="source-box">
    <p class="source-title">📂 Dataset Source Reference</p>
    <p class="source-text">
        This application uses a <strong style="color:#E8E8F0;">synthetic Indian e-commerce dataset</strong>
        modeled after real Indian marketplace sales data available on Kaggle.
        <br/><br/>
        <strong style="color:#F7931E;">Primary Reference Dataset:</strong><br/>
        &nbsp;&nbsp;&#128279; Title&nbsp;&nbsp;: Amazon Sales Report (India) — E-Commerce Sales Dataset<br/>
        &nbsp;&nbsp;&#128279; URL&nbsp;&nbsp;&nbsp;&nbsp;: <a class="source-link"
            href="https://www.kaggle.com/datasets/thedevastator/unlock-profits-with-e-commerce-sales-data"
            target="_blank">kaggle.com/datasets/thedevastator/unlock-profits-with-e-commerce-sales-data</a><br/>
        &nbsp;&nbsp;&#128279; License: CC0 — Public Domain<br/>
        <br/>
        <strong style="color:#F7931E;">Secondary Reference:</strong><br/>
        &nbsp;&nbsp;&#128279; Title&nbsp;&nbsp;: E-Commerce Data (India)<br/>
        &nbsp;&nbsp;&#128279; URL&nbsp;&nbsp;&nbsp;&nbsp;: <a class="source-link"
            href="https://www.kaggle.com/datasets/benroshan/ecommerce-data"
            target="_blank">kaggle.com/datasets/benroshan/ecommerce-data</a><br/>
        &nbsp;&nbsp;&#128279; Author&nbsp;: Ben Roshan<br/>
        <br/>
        <strong style="color:#E8E8F0;">What this dataset captures:</strong><br/>
        The synthetic data has <strong style="color:#FF6B35;">10,000 Indian e-commerce orders</strong>
        spanning <strong style="color:#FF6B35;">January 2020 – December 2023</strong> with realistic:
        <ul style="color:#9CA3AF;margin:8px 0 0 0;padding-left:20px;line-height:1.8;">
            <li>Indian states &amp; cities across 5 regions (North, South, East, West, Central)</li>
            <li>INR pricing with GST (18% Electronics, 12% Home, 5% FMCG)</li>
            <li>Festival seasonality — Diwali, Navratri, Holi, Independence Day peaks</li>
            <li>Payment modes — UPI, COD, Credit/Debit Card, Net Banking, EMI</li>
            <li>Indian product categories — Electronics, Sarees, Kurta, FMCG, Cricket gear</li>
            <li>Fulfilment types — Amazon, Flipkart, Meesho, Merchant</li>
        </ul>
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()
st.markdown("""
<div style="text-align:center;color:#4B5563;font-size:0.8rem;padding:8px 0;">
    SalesPro AI &nbsp;|&nbsp; Built with Streamlit &amp; Machine Learning
    &nbsp;|&nbsp; Powered by Prophet &middot; XGBoost &middot; Ridge Regression
    &nbsp;|&nbsp; Data: Kaggle Indian E-Commerce Datasets
</div>
""", unsafe_allow_html=True)
