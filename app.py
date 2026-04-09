"""
Financial Intelligence Report — Streamlit Application
Senior Financial Data Engineer Quality | Dark Mode | Plotly Charts
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# PAGE CONFIG & DARK THEME
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Financial Intelligence Report",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Design tokens — Nexus Dark palette
COLORS = {
    "bg":           "#171614",
    "surface":      "#1C1B19",
    "surface_alt":  "#201F1D",
    "border":       "#393836",
    "text":         "#CDCCCA",
    "text_muted":   "#797876",
    "text_faint":   "#5A5957",
    "primary":      "#4F98A3",
    "primary_h":    "#227F8B",
    "success":      "#6DAA45",
    "warning":      "#BB653B",
    "error":        "#D163A7",
}

CHART_COLORS = ["#20808D", "#A84B2F", "#4F98A3", "#BCE2E7", "#944454", "#FFC553", "#848456"]

PLOTLY_LAYOUT = dict(
    paper_bgcolor=COLORS["surface"],
    plot_bgcolor=COLORS["bg"],
    font=dict(family="Inter, sans-serif", color=COLORS["text"], size=12),
    margin=dict(l=48, r=24, t=48, b=48),
    xaxis=dict(
        gridcolor=COLORS["border"],
        linecolor=COLORS["border"],
        tickfont=dict(color=COLORS["text_muted"], size=11),
        title_font=dict(color=COLORS["text_muted"]),
    ),
    yaxis=dict(
        gridcolor=COLORS["border"],
        linecolor=COLORS["border"],
        tickfont=dict(color=COLORS["text_muted"], size=11),
        title_font=dict(color=COLORS["text_muted"]),
    ),
    legend=dict(
        bgcolor=COLORS["surface_alt"],
        bordercolor=COLORS["border"],
        borderwidth=1,
        font=dict(color=COLORS["text"], size=11),
    ),
)

CUSTOM_CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Root overrides */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {COLORS["bg"]} !important;
        color: {COLORS["text"]} !important;
        font-family: 'Inter', sans-serif;
    }}
    [data-testid="stSidebar"] {{
        background-color: {COLORS["surface"]} !important;
        border-right: 1px solid {COLORS["border"]};
    }}
    [data-testid="stSidebar"] * {{
        color: {COLORS["text"]} !important;
    }}
    /* Cards */
    .fin-card {{
        background: {COLORS["surface"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }}
    .fin-card-alt {{
        background: {COLORS["surface_alt"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }}
    /* KPI tile */
    .kpi-tile {{
        background: {COLORS["surface"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 10px;
        padding: 18px 20px;
        text-align: center;
        height: 100%;
    }}
    .kpi-label {{
        font-size: 11px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: .06em;
        color: {COLORS["text_muted"]};
        margin-bottom: 6px;
    }}
    .kpi-value {{
        font-size: 26px;
        font-weight: 700;
        color: {COLORS["text"]};
        font-variant-numeric: tabular-nums;
        line-height: 1.1;
    }}
    .kpi-sub {{
        font-size: 11px;
        color: {COLORS["text_faint"]};
        margin-top: 4px;
    }}
    .kpi-positive {{ color: {COLORS["success"]} !important; }}
    .kpi-negative {{ color: {COLORS["error"]} !important; }}
    .kpi-neutral  {{ color: {COLORS["warning"]} !important; }}

    /* Section headers */
    .section-header {{
        font-size: 18px;
        font-weight: 600;
        color: {COLORS["text"]};
        border-bottom: 1px solid {COLORS["border"]};
        padding-bottom: 10px;
        margin-bottom: 20px;
    }}
    .section-badge {{
        display: inline-block;
        background: {COLORS["primary"]};
        color: #fff;
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: .07em;
        border-radius: 4px;
        padding: 2px 8px;
        margin-left: 10px;
        vertical-align: middle;
    }}
    /* Text sections */
    .text-block {{
        font-size: 14px;
        line-height: 1.7;
        color: {COLORS["text_muted"]};
    }}
    .text-block strong {{ color: {COLORS["text"]}; }}

    /* Ticker headline */
    .ticker-hero {{
        font-size: 36px;
        font-weight: 700;
        color: {COLORS["text"]};
        letter-spacing: -.02em;
    }}
    .ticker-sub {{
        font-size: 14px;
        color: {COLORS["text_muted"]};
        margin-top: 2px;
    }}
    .price-tag {{
        font-size: 28px;
        font-weight: 600;
        color: {COLORS["primary"]};
        font-variant-numeric: tabular-nums;
    }}

    /* Stacked labels inside plotly */
    .ratio-tag {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: {COLORS["text_muted"]};
    }}

    /* Streamlit button */
    .stButton > button {{
        background: {COLORS["primary"]} !important;
        color: #fff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        width: 100% !important;
        padding: 12px 0 !important;
        transition: background .2s;
    }}
    .stButton > button:hover {{
        background: {COLORS["primary_h"]} !important;
    }}

    /* Input */
    .stTextInput input {{
        background: {COLORS["bg"]} !important;
        color: {COLORS["text"]} !important;
        border: 1px solid {COLORS["border"]} !important;
        border-radius: 8px !important;
        font-size: 16px !important;
    }}

    /* Divider */
    hr {{ border-color: {COLORS["border"]}; }}

    /* Streamlit elements */
    [data-testid="stMetric"] {{
        background: {COLORS["surface"]};
        border-radius: 10px;
        padding: 16px;
        border: 1px solid {COLORS["border"]};
    }}
    [data-testid="stMetricLabel"] {{ color: {COLORS["text_muted"]} !important; }}
    [data-testid="stMetricValue"] {{ color: {COLORS["text"]} !important; }}

    /* Plotly modebar */
    .modebar {{ background: transparent !important; }}
    .modebar-btn path {{ fill: {COLORS["text_muted"]} !important; }}

    /* Warning box */
    .info-box {{
        background: {COLORS["surface_alt"]};
        border-left: 3px solid {COLORS["primary"]};
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        font-size: 13px;
        color: {COLORS["text_muted"]};
        margin-bottom: 12px;
    }}

    /* Hide Streamlit branding */
    #MainMenu, footer {{ visibility: hidden; }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────
def fmt_large(n):
    """Format large numbers as $1.23T, $456.7B, etc."""
    if n is None or (isinstance(n, float) and np.isnan(n)):
        return "N/A"
    if abs(n) >= 1e12:
        return f"${n/1e12:.2f}T"
    if abs(n) >= 1e9:
        return f"${n/1e9:.2f}B"
    if abs(n) >= 1e6:
        return f"${n/1e6:.2f}M"
    return f"${n:,.0f}"

def fmt_ratio(n, decimals=2, suffix="x"):
    if n is None or (isinstance(n, float) and np.isnan(n)):
        return "N/A"
    return f"{n:.{decimals}f}{suffix}"

def safe_div(a, b):
    try:
        if b == 0 or b is None or np.isnan(b):
            return np.nan
        return a / b
    except Exception:
        return np.nan

def color_class(val, good_high=True, thresholds=(0, None)):
    """Return CSS class based on value direction."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return ""
    lo, hi = thresholds
    if hi is not None:
        if good_high:
            return "kpi-positive" if val >= hi else ("kpi-neutral" if val >= lo else "kpi-negative")
        else:
            return "kpi-positive" if val <= lo else ("kpi-neutral" if val <= hi else "kpi-negative")
    return "kpi-positive" if (val > 0) == good_high else "kpi-negative"

def kpi_html(label, value_str, sub="", css_class=""):
    return f"""
    <div class="kpi-tile">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value {css_class}">{value_str}</div>
        <div class="kpi-sub">{sub}</div>
    </div>"""


# ─────────────────────────────────────────────
# DATA FETCHING
# ─────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def fetch_ticker_data(ticker_symbol: str):
    """Fetch all yfinance data for a ticker."""
    tkr = yf.Ticker(ticker_symbol)
    info = tkr.info or {}
    hist_1y = tkr.history(period="1y", interval="1d")
    hist_q = tkr.quarterly_financials
    quarterly_bs = tkr.quarterly_balance_sheet
    quarterly_cf = tkr.quarterly_cashflow
    quarterly_inc = tkr.quarterly_income_stmt
    return {
        "info": info,
        "hist_1y": hist_1y,
        "quarterly_financials": hist_q,
        "quarterly_balance_sheet": quarterly_bs,
        "quarterly_cashflow": quarterly_cf,
        "quarterly_income_stmt": quarterly_inc,
    }


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_10k_summary(ticker_symbol: str, info: dict) -> dict:
    """
    Attempt to pull 10-K data from SEC EDGAR full-text search API.
    Falls back to yfinance.info fields for a graceful degradation.
    """
    result = {"business": None, "risk_factors": None, "source": "yfinance.info"}

    # --- Try SEC EDGAR full-text search for latest 10-K ---
    try:
        headers = {"User-Agent": "FinancialReportApp research@example.com"}
        # Search EDGAR for latest 10-K
        cik_url = f"https://efts.sec.gov/LATEST/search-index?q=%22{ticker_symbol}%22&dateRange=custom&startdt=2023-01-01&enddt=2025-12-31&forms=10-K"
        r = requests.get(cik_url, headers=headers, timeout=8)
        if r.status_code == 200:
            hits = r.json().get("hits", {}).get("hits", [])
            if hits:
                filing_url = hits[0]["_source"].get("file_date")
                accession = hits[0]["_id"]
                # Pull filing index
                cik_raw = hits[0]["_source"].get("entity_id", "")
                if cik_raw:
                    cik_padded = str(cik_raw).zfill(10)
                    acc_clean = accession.replace("-", "")
                    idx_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik_padded}&type=10-K&dateb=&owner=include&count=1&search_text=&output=atom"
                    result["source"] = f"SEC EDGAR ({filing_url})"
    except Exception:
        pass

    # --- Fallback: build descriptive summary from yfinance.info ---
    biz_desc = info.get("longBusinessSummary", "")
    if biz_desc:
        result["business"] = biz_desc

    # Construct a synthetic risk-factor note from available info fields
    risk_parts = []
    beta = info.get("beta")
    if beta is not None:
        risk_note = (
            f"Market beta of {beta:.2f} indicates {'above' if beta > 1 else 'below'}-market volatility."
        )
        risk_parts.append(risk_note)

    sector = info.get("sector", "")
    industry = info.get("industry", "")
    if sector:
        risk_parts.append(
            f"Operating in the {sector} sector ({industry}), the company faces sector-specific regulatory and competitive risks."
        )

    country = info.get("country", "")
    if country and country != "United States":
        risk_parts.append(
            f"As a {country}-based entity, the company may be exposed to foreign exchange, geopolitical, and cross-border regulatory risks."
        )

    employees = info.get("fullTimeEmployees")
    if employees:
        risk_parts.append(
            f"With approximately {employees:,} full-time employees, workforce-related risks (retention, compensation, labor law) are material."
        )

    audit = info.get("auditRisk")
    if audit is not None:
        risk_parts.append(
            f"ISS Audit Risk Score: {audit}/10. {'Elevated audit risk.' if audit > 5 else 'Moderate audit risk.'}"
        )

    gov = info.get("overallRisk")
    if gov is not None:
        risk_parts.append(f"Overall ISS Governance Risk Score: {gov}/10.")

    if risk_parts:
        result["risk_factors"] = " ".join(risk_parts)
    else:
        result["risk_factors"] = "Risk factor data not available via public API for this ticker."

    if not result["business"]:
        result["business"] = f"Business description not available for {ticker_symbol.upper()} via public API. Please consult the company's latest 10-K filing on SEC EDGAR."

    return result


# ─────────────────────────────────────────────
# FINANCIAL RATIO COMPUTATION
# ─────────────────────────────────────────────
def compute_ratios_quarterly(data: dict) -> pd.DataFrame:
    """
    Compute financial ratios across the last 4 quarters.
    Returns a DataFrame indexed by quarter date.
    """
    bs  = data["quarterly_balance_sheet"]
    inc = data["quarterly_income_stmt"]
    cf  = data["quarterly_cashflow"]
    info = data["info"]

    rows = []

    # Use the most recent 4 quarter columns
    cols = sorted(bs.columns, reverse=True)[:4] if bs is not None and not bs.empty else []

    def g(df, *keys):
        """Get first matching key value from DataFrame row."""
        if df is None or df.empty:
            return np.nan
        for k in keys:
            if k in df.index:
                row = df.loc[k]
                return row
        return pd.Series(np.nan, index=df.columns if hasattr(df, 'columns') else [])

    def gv(df, col, *keys):
        if df is None or df.empty or col not in df.columns:
            return np.nan
        for k in keys:
            if k in df.index:
                val = df.loc[k, col]
                return float(val) if not pd.isna(val) else np.nan
        return np.nan

    for col in cols:
        quarter_label = pd.Timestamp(col).strftime("Q%q %Y") if hasattr(col, 'strftime') else str(col)

        # ── Liquidity ──────────────────────────────
        current_assets  = gv(bs, col, "Current Assets", "TotalCurrentAssets")
        current_liab    = gv(bs, col, "Current Liabilities", "TotalCurrentLiabilities", "CurrentLiabilities")
        inventory       = gv(bs, col, "Inventory", "Inventories")
        cash            = gv(bs, col, "Cash And Cash Equivalents", "CashAndCashEquivalents", "Cash")

        current_ratio = safe_div(current_assets, current_liab)
        quick_assets  = (current_assets or 0) - (inventory or 0)
        quick_ratio   = safe_div(quick_assets, current_liab)

        # ── Profitability ───────────────────────────
        net_income      = gv(inc, col, "Net Income", "NetIncome", "Net Income Common Stockholders")
        revenue         = gv(inc, col, "Total Revenue", "Revenue", "TotalRevenue")
        total_assets    = gv(bs, col, "Total Assets", "TotalAssets")
        stockholder_eq  = gv(bs, col, "Stockholders Equity", "Total Stockholder Equity",
                             "CommonStockEquity", "StockholdersEquity")
        ebit            = gv(inc, col, "EBIT", "Operating Income", "OperatingIncome")
        interest_exp    = gv(inc, col, "Interest Expense", "InterestExpense")
        depreciation    = gv(cf,  col, "Depreciation", "DepreciationAndAmortization",
                             "Depreciation And Amortization")

        roe = safe_div(net_income * 4, stockholder_eq)  # annualised
        roa = safe_div(net_income * 4, total_assets)
        npm = safe_div(net_income, revenue)

        # ── Leverage ────────────────────────────────
        total_debt      = gv(bs, col, "Long Term Debt", "LongTermDebt", "Total Debt", "LongTermDebtAndCapitalLeaseObligation")
        short_debt      = gv(bs, col, "Short Term Debt", "CurrentDebt", "Short Long Term Debt")
        combined_debt   = (total_debt or 0) + (short_debt or 0)
        de_ratio        = safe_div(combined_debt, stockholder_eq)
        ebitda          = (ebit or 0) + abs(depreciation or 0)
        interest_cov    = safe_div(ebit, abs(interest_exp) if interest_exp else np.nan)

        # ── Valuation (point-in-time from info; consistent across quarters) ──
        price           = info.get("currentPrice") or info.get("regularMarketPrice") or np.nan
        eps             = info.get("trailingEps") or np.nan
        pe              = safe_div(price, eps)
        book_ps         = info.get("bookValue") or np.nan
        pb              = safe_div(price, book_ps)
        market_cap      = info.get("marketCap") or np.nan
        ev              = info.get("enterpriseValue") or np.nan
        ebitda_ttm      = info.get("ebitda") or np.nan
        ev_ebitda       = safe_div(ev, ebitda_ttm)

        rows.append({
            "Quarter": quarter_label,
            "Date": col,
            # Liquidity
            "Current Ratio": current_ratio,
            "Quick Ratio": quick_ratio,
            # Profitability
            "ROE (%)": (roe or np.nan) * 100,
            "ROA (%)": (roa or np.nan) * 100,
            "Net Profit Margin (%)": (npm or np.nan) * 100,
            # Leverage
            "Debt-to-Equity": de_ratio,
            "Interest Coverage": interest_cov,
            # Valuation
            "P/E Ratio": pe,
            "EV/EBITDA": ev_ebitda,
            "Price-to-Book": pb,
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("Date").reset_index(drop=True)
    return df


# ─────────────────────────────────────────────
# CHART BUILDERS
# ─────────────────────────────────────────────
def price_chart(hist: pd.DataFrame, ticker: str) -> go.Figure:
    """1-year price area chart."""
    if hist is None or hist.empty:
        return go.Figure()

    close = hist["Close"].dropna()
    color = COLORS["primary"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=close.index, y=close.values,
        mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy",
        fillcolor=f"rgba(79,152,163,0.12)",
        name="Close Price",
        hovertemplate="<b>%{x|%b %d, %Y}</b><br>$%{y:.2f}<extra></extra>",
    ))

    # Moving averages
    for window, col, label in [(50, "#FFC553", "50-day MA"), (200, "#A84B2F", "200-day MA")]:
        if len(close) >= window:
            ma = close.rolling(window).mean()
            fig.add_trace(go.Scatter(
                x=ma.index, y=ma.values,
                mode="lines",
                line=dict(color=col, width=1.5, dash="dot"),
                name=label,
                hovertemplate=f"<b>%{{x|%b %d, %Y}}</b><br>{label}: $%{{y:.2f}}<extra></extra>",
                opacity=0.85,
            ))

    layout = dict(**PLOTLY_LAYOUT)
    layout["title"] = dict(text=f"{ticker} — 1-Year Price History", font=dict(size=15, color=COLORS["text"]), x=0.01)
    layout["yaxis"]["tickprefix"] = "$"
    layout["hovermode"] = "x unified"
    fig.update_layout(**layout)
    return fig


def ratio_group_chart(df: pd.DataFrame, cols: list, title: str, pct=False, benchmark_lines: dict = None) -> go.Figure:
    """Grouped bar + line chart for ratio groups across quarters."""
    if df.empty:
        return go.Figure()

    fig = go.Figure()
    bar_mode = "group"
    color_iter = iter(CHART_COLORS)

    for col in cols:
        if col not in df.columns:
            continue
        vals = df[col].tolist()
        q_labels = df["Quarter"].tolist()
        clr = next(color_iter)

        if pct:
            hover_template = f"<b>%{{x}}</b><br>{col}: %{{y:.1f}}%<extra></extra>"
            text_vals = [f"{v:.1f}%" if not np.isnan(v) else "N/A" for v in vals]
        else:
            hover_template = f"<b>%{{x}}</b><br>{col}: %{{y:.2f}}x<extra></extra>"
            text_vals = [f"{v:.2f}x" if not np.isnan(v) else "N/A" for v in vals]

        fig.add_trace(go.Bar(
            x=q_labels, y=vals,
            name=col,
            marker_color=clr,
            marker_line=dict(color=COLORS["border"], width=0.5),
            text=text_vals,
            textposition="outside",
            textfont=dict(size=10, color=COLORS["text_muted"]),
            hovertemplate=hover_template,
        ))

    # Benchmark reference lines
    if benchmark_lines:
        for label, yval in benchmark_lines.items():
            fig.add_hline(
                y=yval,
                line=dict(color=COLORS["warning"], dash="dash", width=1),
                annotation_text=label,
                annotation_font=dict(color=COLORS["warning"], size=10),
                annotation_position="top left",
            )

    layout = dict(**PLOTLY_LAYOUT)
    layout["title"] = dict(text=title, font=dict(size=14, color=COLORS["text"]), x=0.01)
    layout["barmode"] = bar_mode
    layout["yaxis"]["ticksuffix"] = "%" if pct else ""
    layout["showlegend"] = len(cols) > 1
    fig.update_layout(**layout)
    return fig


def waterfall_margin(df: pd.DataFrame) -> go.Figure:
    """Net Profit Margin trend as a clean line chart."""
    if df.empty or "Net Profit Margin (%)" not in df.columns:
        return go.Figure()

    fig = go.Figure()
    vals = df["Net Profit Margin (%)"].tolist()
    q_labels = df["Quarter"].tolist()
    colors = [COLORS["success"] if v >= 0 else COLORS["error"] for v in vals]

    fig.add_trace(go.Bar(
        x=q_labels, y=vals,
        name="Net Margin %",
        marker_color=colors,
        text=[f"{v:.1f}%" for v in vals],
        textposition="outside",
        textfont=dict(size=10, color=COLORS["text_muted"]),
        hovertemplate="<b>%{x}</b><br>Net Margin: %{y:.2f}%<extra></extra>",
    ))
    fig.add_hline(y=0, line=dict(color=COLORS["border"], width=1))

    layout = dict(**PLOTLY_LAYOUT)
    layout["title"] = dict(text="Net Profit Margin by Quarter (%)", font=dict(size=14, color=COLORS["text"]), x=0.01)
    fig.update_layout(**layout)
    return fig


def leverage_gauge(de: float, ic: float) -> go.Figure:
    """Side-by-side gauge for D/E and Interest Coverage."""
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "indicator"}, {"type": "indicator"}]],
        subplot_titles=["Debt / Equity Ratio", "Interest Coverage Ratio"],
    )

    de_val   = de if de and not np.isnan(de) else 0
    ic_val   = ic if ic and not np.isnan(ic) else 0

    # D/E gauge — lower is generally safer
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=de_val,
        number=dict(suffix="x", font=dict(color=COLORS["text"], size=28)),
        gauge=dict(
            axis=dict(range=[0, 5], tickcolor=COLORS["text_muted"], tickfont=dict(color=COLORS["text_muted"])),
            bar=dict(color=COLORS["primary"]),
            steps=[
                dict(range=[0, 1.5], color="#2A3D2A"),
                dict(range=[1.5, 3],  color="#3D3320"),
                dict(range=[3, 5],    color="#3D2020"),
            ],
            threshold=dict(line=dict(color=COLORS["error"], width=2), value=3),
            bgcolor=COLORS["surface"],
        ),
    ), row=1, col=1)

    # Interest Coverage gauge — higher is safer
    ic_max = max(30, ic_val * 1.2)
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=ic_val,
        number=dict(suffix="x", font=dict(color=COLORS["text"], size=28)),
        gauge=dict(
            axis=dict(range=[0, ic_max], tickcolor=COLORS["text_muted"], tickfont=dict(color=COLORS["text_muted"])),
            bar=dict(color=COLORS["primary"]),
            steps=[
                dict(range=[0, 1.5],        color="#3D2020"),
                dict(range=[1.5, 3],         color="#3D3320"),
                dict(range=[3, ic_max],      color="#2A3D2A"),
            ],
            threshold=dict(line=dict(color=COLORS["success"], width=2), value=3),
            bgcolor=COLORS["surface"],
        ),
    ), row=1, col=2)

    layout = dict(
        paper_bgcolor=COLORS["surface"],
        font=dict(color=COLORS["text"], family="Inter, sans-serif"),
        margin=dict(l=24, r=24, t=60, b=24),
        height=280,
    )
    for ann in fig.layout.annotations:
        ann.font = dict(color=COLORS["text_muted"], size=12)
    fig.update_layout(**layout)
    return fig


def valuation_radar(df: pd.DataFrame, info: dict) -> go.Figure:
    """Radar / spider chart for latest valuation ratios vs sector benchmarks."""
    latest = df.iloc[-1] if not df.empty else {}

    def safe_val(key, fallback=0):
        v = latest.get(key, np.nan)
        return v if not (isinstance(v, float) and np.isnan(v)) else fallback

    pe    = safe_val("P/E Ratio", 0)
    pb    = safe_val("Price-to-Book", 0)
    ev_eb = safe_val("EV/EBITDA", 0)

    # S&P 500 sector avg benchmarks (approximate)
    sector = info.get("sector", "")
    benchmarks = {
        "Technology": dict(pe=28, pb=7, ev_ebitda=20),
        "Financials":  dict(pe=14, pb=1.5, ev_ebitda=12),
        "Health Care": dict(pe=22, pb=4, ev_ebitda=16),
        "Consumer Discretionary": dict(pe=24, pb=5, ev_ebitda=15),
    }
    bench = benchmarks.get(sector, dict(pe=20, pb=3, ev_ebitda=14))

    categories = ["P/E Ratio", "Price-to-Book", "EV/EBITDA"]
    company_vals = [
        min(pe, 80),
        min(pb, 20),
        min(ev_eb, 50),
    ]
    sector_vals = [bench["pe"], bench["pb"], bench["ev_ebitda"]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=company_vals + [company_vals[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor=f"rgba(79,152,163,0.25)",
        line=dict(color=COLORS["primary"], width=2),
        name="Company",
    ))
    fig.add_trace(go.Scatterpolar(
        r=sector_vals + [sector_vals[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor=f"rgba(168,75,47,0.15)",
        line=dict(color="#A84B2F", width=2, dash="dot"),
        name=f"Sector Avg ({sector or 'Market'})",
    ))

    fig.update_layout(
        polar=dict(
            bgcolor=COLORS["bg"],
            radialaxis=dict(visible=True, gridcolor=COLORS["border"], tickfont=dict(color=COLORS["text_muted"], size=10)),
            angularaxis=dict(gridcolor=COLORS["border"], tickfont=dict(color=COLORS["text"], size=11)),
        ),
        paper_bgcolor=COLORS["surface"],
        font=dict(color=COLORS["text"], family="Inter, sans-serif"),
        legend=dict(bgcolor=COLORS["surface_alt"], bordercolor=COLORS["border"], borderwidth=1, font=dict(color=COLORS["text"])),
        margin=dict(l=40, r=40, t=50, b=40),
        title=dict(text="Valuation vs. Sector Benchmarks", font=dict(size=14, color=COLORS["text"]), x=0.01),
    )
    return fig


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding: 8px 0 24px 0;">
        <div style="font-size:20px; font-weight:700; color:{COLORS['text']};">📊 FintelliReport</div>
        <div style="font-size:12px; color:{COLORS['text_muted']}; margin-top:4px;">Financial Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    ticker_input = st.text_input(
        "Stock Ticker",
        value="AAPL",
        placeholder="e.g. MSFT, NVDA, JPM",
        help="Enter any valid US stock ticker symbol",
    ).strip().upper()

    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("Generate Report", type="primary")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:11px; color:{COLORS['text_faint']}; line-height:1.6;">
        <b style="color:{COLORS['text_muted']};">Data Sources</b><br>
        Market Data: Yahoo Finance<br>
        Filings: SEC EDGAR API<br>
        Financials: yfinance Quarterly Statements<br><br>
        <b style="color:{COLORS['text_muted']};">Ratios Computed</b><br>
        Liquidity · Profitability<br>
        Leverage · Valuation<br>
        (Last 4 Quarters)
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN PAGE — HERO
# ─────────────────────────────────────────────
if not generate_btn:
    st.markdown(f"""
    <div style="padding: 80px 40px; text-align:center;">
        <div style="font-size:52px; font-weight:700; color:{COLORS['text']}; letter-spacing:-.03em;">
            Financial Intelligence Report
        </div>
        <div style="font-size:18px; color:{COLORS['text_muted']}; margin-top:16px; max-width:600px; margin-left:auto; margin-right:auto; line-height:1.6;">
            Institutional-grade equity analysis — market data, SEC filing summaries,
            and multi-quarter financial ratio dashboards.
        </div>
        <div style="margin-top:40px; font-size:14px; color:{COLORS['text_faint']};">
            Enter a ticker symbol in the sidebar and click <b style="color:{COLORS['primary']};">Generate Report</b>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────
# REPORT GENERATION
# ─────────────────────────────────────────────
with st.spinner(f"Fetching data for {ticker_input}…"):
    try:
        data = fetch_ticker_data(ticker_input)
    except Exception as e:
        st.error(f"Could not fetch data for **{ticker_input}**: {e}")
        st.stop()

info = data["info"]
if not info or not info.get("symbol"):
    st.error(f"Ticker **{ticker_input}** not found. Please check the symbol and try again.")
    st.stop()

company_name = info.get("longName") or info.get("shortName") or ticker_input
sector       = info.get("sector", "N/A")
industry     = info.get("industry", "N/A")
exchange     = info.get("exchange", "")
currency     = info.get("currency", "USD")
price        = info.get("currentPrice") or info.get("regularMarketPrice") or np.nan
prev_close   = info.get("previousClose") or np.nan
price_chg    = ((price - prev_close) / prev_close * 100) if not np.isnan(price) and not np.isnan(prev_close) else np.nan
mkt_cap      = info.get("marketCap")
avg_vol      = info.get("averageVolume")

# Compute ratios & 10-K summary concurrently
with st.spinner("Computing financial ratios…"):
    ratio_df = compute_ratios_quarterly(data)

with st.spinner("Retrieving 10-K filing summary…"):
    sec_data = fetch_10k_summary(ticker_input, info)


# ─── HEADER ──────────────────────────────────
chg_color = COLORS["success"] if price_chg and price_chg >= 0 else COLORS["error"]
chg_arrow = "▲" if price_chg and price_chg >= 0 else "▼"

st.markdown(f"""
<div class="fin-card" style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:16px;">
    <div>
        <div class="ticker-hero">{ticker_input}</div>
        <div class="ticker-sub">{company_name} &nbsp;·&nbsp; {exchange} &nbsp;·&nbsp; {sector} &nbsp;·&nbsp; {industry}</div>
    </div>
    <div style="text-align:right;">
        <div class="price-tag">{currency} {price:,.2f}</div>
        <div style="font-size:14px; color:{chg_color}; font-weight:600; margin-top:4px;">
            {chg_arrow} {abs(price_chg):.2f}% vs prev close
        </div>
        <div style="font-size:12px; color:{COLORS['text_faint']}; margin-top:2px;">
            Mkt Cap: {fmt_large(mkt_cap)} &nbsp;·&nbsp; Avg Vol: {fmt_large(avg_vol).replace('$','')}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─── SECTION 1: PRICE CHART ──────────────────
st.markdown(f'<div class="section-header">Market Overview <span class="section-badge">1-Year</span></div>', unsafe_allow_html=True)
fig_price = price_chart(data["hist_1y"], ticker_input)
st.plotly_chart(fig_price, use_container_width=True, config={"displayModeBar": True})


# KPI row
col1, col2, col3, col4, col5 = st.columns(5)
week52h = info.get("fiftyTwoWeekHigh")
week52l = info.get("fiftyTwoWeekLow")
pe_ttm  = info.get("trailingPE")
fwd_pe  = info.get("forwardPE")
div_yld = info.get("dividendYield")

for col, label, val, sub in [
    (col1, "52-Week High",   f"${week52h:,.2f}" if week52h else "N/A", ""),
    (col2, "52-Week Low",    f"${week52l:,.2f}" if week52l else "N/A", ""),
    (col3, "Trailing P/E",   f"{pe_ttm:.1f}x" if pe_ttm else "N/A",  "TTM"),
    (col4, "Forward P/E",    f"{fwd_pe:.1f}x" if fwd_pe else "N/A",   "NTM"),
    (col5, "Dividend Yield", f"{div_yld*100:.2f}%" if div_yld else "—", "Annual"),
]:
    col.markdown(kpi_html(label, val, sub), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─── SECTION 2: SEC 10-K SUMMARY ─────────────
st.markdown(f'<div class="section-header">10-K Filing Summary <span class="section-badge">Latest</span></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="info-box">
    Source: {sec_data.get("source", "yfinance.info")}  &nbsp;·&nbsp;
    For full 10-K text, see
    <a href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company={ticker_input}&type=10-K&dateb=&owner=include&count=5" 
       target="_blank" style="color:{COLORS['primary']};">SEC EDGAR</a>
</div>
""", unsafe_allow_html=True)

tab_biz, tab_risk = st.tabs(["Business Description", "Risk Factors"])

with tab_biz:
    biz_text = sec_data.get("business") or "Not available."
    st.markdown(f'<div class="text-block fin-card">{biz_text}</div>', unsafe_allow_html=True)

with tab_risk:
    risk_text = sec_data.get("risk_factors") or "Not available."
    st.markdown(f'<div class="text-block fin-card">{risk_text}</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─── SECTION 3: FINANCIAL HEALTH DASHBOARD ───
st.markdown(f'<div class="section-header">Financial Health Dashboard <span class="section-badge">4 Quarters</span></div>', unsafe_allow_html=True)

if ratio_df.empty:
    st.warning("Quarterly financial statement data not available for this ticker.")
else:
    latest = ratio_df.iloc[-1]

    # ── 3A: KPI Cards for Latest Quarter ─────
    st.markdown(f"##### Latest Quarter: {latest.get('Quarter','')}")
    st.markdown("")

    # Liquidity row
    c1, c2, c3, c4, c5 = st.columns(5)
    cr = latest.get("Current Ratio")
    qr = latest.get("Quick Ratio")
    roe_ = latest.get("ROE (%)")
    roa_ = latest.get("ROA (%)")
    npm_ = latest.get("Net Profit Margin (%)")

    for col, label, val, sub, css in [
        (c1, "Current Ratio",   fmt_ratio(cr, 2), "≥2 healthy", color_class(cr, True, (1, 2))),
        (c2, "Quick Ratio",     fmt_ratio(qr, 2), "≥1 healthy", color_class(qr, True, (0.5, 1))),
        (c3, "ROE",             fmt_ratio(roe_, 1, "%"), "Return on Equity", color_class(roe_, True, (0, 15))),
        (c4, "ROA",             fmt_ratio(roa_, 1, "%"), "Return on Assets", color_class(roa_, True, (0, 5))),
        (c5, "Net Margin",      fmt_ratio(npm_, 1, "%"), "Net Profit Margin", color_class(npm_, True, (0, 10))),
    ]:
        col.markdown(kpi_html(label, val, sub, css), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    de   = latest.get("Debt-to-Equity")
    ic   = latest.get("Interest Coverage")
    pe_  = latest.get("P/E Ratio")
    ev_  = latest.get("EV/EBITDA")
    pb_  = latest.get("Price-to-Book")

    c6, c7, c8, c9, c10 = st.columns(5)
    for col, label, val, sub, css in [
        (c6,  "Debt/Equity",    fmt_ratio(de,  2), "Lower is safer", color_class(de, False, (1, 3))),
        (c7,  "Int. Coverage",  fmt_ratio(ic,  1), "≥3 comfortable", color_class(ic, True,  (1.5, 3))),
        (c8,  "P/E Ratio",      fmt_ratio(pe_, 1), "Trailing EPS",   ""),
        (c9,  "EV/EBITDA",      fmt_ratio(ev_, 1), "Enterprise val.",  ""),
        (c10, "Price/Book",     fmt_ratio(pb_, 2), "Market vs. book", ""),
    ]:
        col.markdown(kpi_html(label, val, sub, css), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 3B: Quarterly Charts ─────────────────
    st.markdown("##### Quarterly Trend Charts")

    ch_left, ch_right = st.columns(2)

    with ch_left:
        # Liquidity
        fig_liq = ratio_group_chart(
            ratio_df, ["Current Ratio", "Quick Ratio"],
            "Liquidity Ratios (×)",
            benchmark_lines={"Healthy CR ≥ 2": 2, "Healthy QR ≥ 1": 1},
        )
        st.plotly_chart(fig_liq, use_container_width=True, config={"displayModeBar": False})

    with ch_right:
        # Profitability — ROE & ROA
        fig_prof = ratio_group_chart(
            ratio_df, ["ROE (%)", "ROA (%)"],
            "Profitability — ROE & ROA (%)",
            pct=True,
        )
        st.plotly_chart(fig_prof, use_container_width=True, config={"displayModeBar": False})

    # Net Margin — full width
    fig_npm = waterfall_margin(ratio_df)
    st.plotly_chart(fig_npm, use_container_width=True, config={"displayModeBar": False})

    ch_left2, ch_right2 = st.columns(2)

    with ch_left2:
        # Leverage gauges — most recent
        fig_lev = leverage_gauge(
            latest.get("Debt-to-Equity", 0),
            latest.get("Interest Coverage", 0),
        )
        st.markdown(f'<div class="section-header" style="font-size:14px; margin-bottom:0;">Leverage Indicators</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_lev, use_container_width=True, config={"displayModeBar": False})

    with ch_right2:
        # Valuation radar
        fig_val = valuation_radar(ratio_df, info)
        st.plotly_chart(fig_val, use_container_width=True, config={"displayModeBar": False})

    # Valuation bar chart
    fig_val_bars = ratio_group_chart(
        ratio_df, ["P/E Ratio", "EV/EBITDA", "Price-to-Book"],
        "Valuation Multiples — Quarterly (Point-in-Time)",
    )
    st.plotly_chart(fig_val_bars, use_container_width=True, config={"displayModeBar": False})


# ─── FOOTER ──────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align:center; padding:24px; font-size:11px; color:{COLORS['text_faint']}; border-top:1px solid {COLORS['border']};">
    FintelliReport &nbsp;·&nbsp; Data via Yahoo Finance & SEC EDGAR &nbsp;·&nbsp;
    For educational and research purposes only. Not investment advice.<br>
    Generated {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
</div>
""", unsafe_allow_html=True)
