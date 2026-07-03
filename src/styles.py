"""
Shared Premium CSS for India Sales Forecasting System
=======================================================
Import and call inject_css() at the top of any Streamlit page.
"""


def get_css() -> str:
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ═══════════════════════════════════════════════════════════
   GLOBAL RESET & BASE
═══════════════════════════════════════════════════════════ */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
}
.stApp {
    background: #0C0C16;
}

/* ═══════════════════════════════════════════════════════════
   SIDEBAR — NAVBAR
═══════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F0F1A 0%, #13131F 60%, #0F0F1A 100%) !important;
    border-right: 1px solid rgba(255, 107, 53, 0.18) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}

/* Sidebar top logo area */
[data-testid="stSidebarNav"] {
    padding-top: 0 !important;
}

/* Nav links container */
[data-testid="stSidebarNav"] ul {
    padding: 0 12px !important;
    gap: 4px !important;
    display: flex;
    flex-direction: column;
}

/* Each nav link */
[data-testid="stSidebarNav"] a {
    display: flex !important;
    align-items: center !important;
    padding: 10px 14px !important;
    border-radius: 10px !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: #9CA3AF !important;
    text-decoration: none !important;
    transition: all 0.2s ease !important;
    border: 1px solid transparent !important;
    margin-bottom: 2px !important;
}
[data-testid="stSidebarNav"] a:hover {
    background: rgba(255, 107, 53, 0.10) !important;
    color: #FF6B35 !important;
    border-color: rgba(255, 107, 53, 0.25) !important;
    transform: translateX(3px) !important;
}
/* Active nav link */
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: linear-gradient(135deg, rgba(255,107,53,0.18), rgba(247,147,30,0.12)) !important;
    color: #FF6B35 !important;
    border-color: rgba(255, 107, 53, 0.4) !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 12px rgba(255,107,53,0.15) !important;
}

/* Sidebar divider */
[data-testid="stSidebar"] hr {
    border-color: rgba(255,107,53,0.15) !important;
    margin: 12px 0 !important;
}

/* Sidebar section labels */
[data-testid="stSidebar"] .stMarkdown p {
    color: #6B7280 !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.6px !important;
}
[data-testid="stSidebar"] .stMarkdown strong {
    color: #9CA3AF !important;
    font-size: 0.82rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

/* ═══════════════════════════════════════════════════════════
   SELECTBOX / DROPDOWN
═══════════════════════════════════════════════════════════ */
[data-testid="stSelectbox"] > div > div {
    background: #1A1A2E !important;
    border: 1px solid rgba(255,107,53,0.25) !important;
    border-radius: 10px !important;
    color: #E8E8F0 !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stSelectbox"] > div > div:hover {
    border-color: rgba(255,107,53,0.5) !important;
    box-shadow: 0 0 0 3px rgba(255,107,53,0.08) !important;
}
[data-testid="stSelectbox"] label {
    color: #9CA3AF !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    margin-bottom: 4px !important;
}
/* Dropdown arrow */
[data-testid="stSelectbox"] svg {
    color: #FF6B35 !important;
    fill: #FF6B35 !important;
}

/* ═══════════════════════════════════════════════════════════
   MULTISELECT
═══════════════════════════════════════════════════════════ */
[data-testid="stMultiSelect"] > div > div {
    background: #1A1A2E !important;
    border: 1px solid rgba(255,107,53,0.25) !important;
    border-radius: 10px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stMultiSelect"] > div > div:hover {
    border-color: rgba(255,107,53,0.5) !important;
}
[data-testid="stMultiSelect"] label {
    color: #9CA3AF !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}
/* Tags */
[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background: linear-gradient(135deg, rgba(255,107,53,0.25), rgba(247,147,30,0.2)) !important;
    border: 1px solid rgba(255,107,53,0.35) !important;
    border-radius: 6px !important;
    color: #FF6B35 !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
}

/* ═══════════════════════════════════════════════════════════
   DATE INPUT
═══════════════════════════════════════════════════════════ */
[data-testid="stDateInput"] > div > div > input {
    background: #1A1A2E !important;
    border: 1px solid rgba(255,107,53,0.25) !important;
    border-radius: 10px !important;
    color: #E8E8F0 !important;
    padding: 8px 12px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stDateInput"] > div > div > input:focus {
    border-color: #FF6B35 !important;
    box-shadow: 0 0 0 3px rgba(255,107,53,0.12) !important;
    outline: none !important;
}
[data-testid="stDateInput"] label {
    color: #9CA3AF !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

/* ═══════════════════════════════════════════════════════════
   SLIDER
═══════════════════════════════════════════════════════════ */
[data-testid="stSlider"] label {
    color: #9CA3AF !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}
/* Track */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background: #FF6B35 !important;
    border: 2px solid #FF6B35 !important;
    box-shadow: 0 0 8px rgba(255,107,53,0.5) !important;
    width: 18px !important;
    height: 18px !important;
}
/* Filled track */
[data-testid="stSlider"] [data-testid="stTickBar"] + div > div > div:first-child {
    background: linear-gradient(90deg, #FF6B35, #F7931E) !important;
}
/* Slider value label */
[data-testid="stSlider"] [data-baseweb="slider"] > div:last-child div {
    background: #FF6B35 !important;
    color: white !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    font-size: 0.78rem !important;
}

/* ═══════════════════════════════════════════════════════════
   RADIO BUTTONS
═══════════════════════════════════════════════════════════ */
[data-testid="stRadio"] label {
    color: #9CA3AF !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}
[data-testid="stRadio"] div[role="radiogroup"] > label {
    background: #1A1A2E !important;
    border: 1px solid rgba(255,107,53,0.2) !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    margin-bottom: 6px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    text-transform: none !important;
    letter-spacing: normal !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: #C4C4D4 !important;
    width: 100% !important;
}
[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
    border-color: rgba(255,107,53,0.45) !important;
    background: rgba(255,107,53,0.07) !important;
    color: #FF6B35 !important;
}
/* Selected radio */
[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
    background: linear-gradient(135deg, rgba(255,107,53,0.18), rgba(247,147,30,0.12)) !important;
    border-color: rgba(255,107,53,0.5) !important;
    color: #FF6B35 !important;
    font-weight: 700 !important;
}
/* Radio dot */
[data-testid="stRadio"] input[type="radio"]:checked + div {
    background: #FF6B35 !important;
    border-color: #FF6B35 !important;
}

/* ═══════════════════════════════════════════════════════════
   BUTTONS
═══════════════════════════════════════════════════════════ */
/* Primary */
div.stButton > button[kind="primary"],
div.stButton > button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 12px 24px !important;
    letter-spacing: 0.3px !important;
    box-shadow: 0 4px 16px rgba(255,107,53,0.35) !important;
    transition: all 0.2s ease !important;
}
div.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 22px rgba(255,107,53,0.48) !important;
    opacity: 0.93 !important;
}
/* Secondary / default */
div.stButton > button:not([kind="primary"]) {
    background: rgba(26,26,46,0.9) !important;
    border: 1px solid rgba(255,107,53,0.3) !important;
    border-radius: 10px !important;
    color: #E8E8F0 !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
div.stButton > button:not([kind="primary"]):hover {
    border-color: #FF6B35 !important;
    color: #FF6B35 !important;
    background: rgba(255,107,53,0.07) !important;
}

/* Download buttons */
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, rgba(255,107,53,0.15), rgba(247,147,30,0.1)) !important;
    border: 1px solid rgba(255,107,53,0.4) !important;
    border-radius: 10px !important;
    color: #FF6B35 !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: linear-gradient(135deg, rgba(255,107,53,0.25), rgba(247,147,30,0.18)) !important;
    box-shadow: 0 4px 14px rgba(255,107,53,0.25) !important;
    transform: translateY(-1px) !important;
}

/* ═══════════════════════════════════════════════════════════
   METRIC CARDS (st.metric)
═══════════════════════════════════════════════════════════ */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #1A1A2E, #16213E) !important;
    border: 1px solid rgba(255,107,53,0.22) !important;
    border-radius: 14px !important;
    padding: 16px !important;
}
[data-testid="stMetricLabel"] {
    color: #9CA3AF !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}
[data-testid="stMetricValue"] {
    color: #FF6B35 !important;
    font-weight: 800 !important;
}

/* ═══════════════════════════════════════════════════════════
   EXPANDER
═══════════════════════════════════════════════════════════ */
[data-testid="stExpander"] {
    background: #1A1A2E !important;
    border: 1px solid rgba(255,107,53,0.2) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    color: #C4C4D4 !important;
    font-weight: 600 !important;
    padding: 14px 18px !important;
    transition: color 0.2s !important;
}
[data-testid="stExpander"] summary:hover {
    color: #FF6B35 !important;
}
[data-testid="stExpander"] svg {
    color: #FF6B35 !important;
    fill: #FF6B35 !important;
}

/* ═══════════════════════════════════════════════════════════
   INFO / WARNING / ERROR ALERTS
═══════════════════════════════════════════════════════════ */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border-left-width: 4px !important;
    font-size: 0.88rem !important;
}
/* Info */
.stAlert[data-baseweb="notification"][kind="info"],
div[data-testid="stAlert"] > div[class*="info"] {
    background: rgba(59,130,246,0.08) !important;
    border-color: #3B82F6 !important;
}
/* Warning */
div[data-testid="stAlert"] > div[class*="warning"] {
    background: rgba(247,147,30,0.08) !important;
    border-color: #F7931E !important;
}

/* ═══════════════════════════════════════════════════════════
   DATAFRAME / TABLE
═══════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,107,53,0.18) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] table {
    border-collapse: separate !important;
    border-spacing: 0 !important;
}
[data-testid="stDataFrame"] th {
    background: linear-gradient(135deg, #1A1A2E, #16213E) !important;
    color: #FF6B35 !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    border-bottom: 1px solid rgba(255,107,53,0.2) !important;
    padding: 12px 16px !important;
}
[data-testid="stDataFrame"] td {
    background: #13131F !important;
    color: #C4C4D4 !important;
    border-bottom: 1px solid rgba(255,255,255,0.04) !important;
    padding: 10px 16px !important;
    font-size: 0.87rem !important;
}
[data-testid="stDataFrame"] tr:hover td {
    background: rgba(255,107,53,0.05) !important;
}

/* ═══════════════════════════════════════════════════════════
   SPINNER
═══════════════════════════════════════════════════════════ */
[data-testid="stSpinner"] > div {
    border-top-color: #FF6B35 !important;
}

/* ═══════════════════════════════════════════════════════════
   SCROLLBAR
═══════════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0F0F1A; }
::-webkit-scrollbar-thumb {
    background: rgba(255,107,53,0.35);
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(255,107,53,0.6); }

/* ═══════════════════════════════════════════════════════════
   DIVIDER
═══════════════════════════════════════════════════════════ */
hr {
    border-color: rgba(255,107,53,0.15) !important;
    margin: 20px 0 !important;
}

/* ═══════════════════════════════════════════════════════════
   SECTION HEADER (shared class)
═══════════════════════════════════════════════════════════ */
.section-header {
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    color: #E8E8F0 !important;
    margin: 28px 0 14px 0 !important;
    padding-bottom: 10px !important;
    border-bottom: 1px solid rgba(255,107,53,0.22) !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
}

/* ═══════════════════════════════════════════════════════════
   PAGE HEADER CARD
═══════════════════════════════════════════════════════════ */
.page-header {
    background: linear-gradient(135deg, #1A1A2E 0%, #16213E 100%) !important;
    border: 1px solid rgba(255,107,53,0.28) !important;
    border-radius: 18px !important;
    padding: 30px 36px !important;
    margin-bottom: 28px !important;
    position: relative !important;
    overflow: hidden !important;
}
.page-header::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(255,107,53,0.08), transparent 70%);
    border-radius: 50%;
}

/* ═══════════════════════════════════════════════════════════
   COLUMN GAPS — tighter layout
═══════════════════════════════════════════════════════════ */
[data-testid="column"] {
    padding: 0 6px !important;
}

</style>
"""


def inject_css():
    import streamlit as st
    st.markdown(get_css(), unsafe_allow_html=True)
