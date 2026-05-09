"""
TSP Fertilizer Production Dashboard
====================================
Final Year Project - Decision Support Tool
Triple Super Phosphate (TSP) production from rock phosphate + sulfuric acid.

Run with:
    pip install streamlit plotly
    streamlit run tsp_dashboard.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="TSP Production Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    /* Dark industrial theme */
    .stApp {
        background-color: #0f1117;
        color: #e0e6f0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b27;
        border-right: 1px solid #2a3145;
    }
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #7dd3b0;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        border-bottom: 1px solid #2a3145;
        padding-bottom: 6px;
        margin-top: 20px;
    }

    /* KPI cards */
    .kpi-card {
        background: linear-gradient(135deg, #1a2035, #1e2740);
        border: 1px solid #2a3a5c;
        border-radius: 10px;
        padding: 18px 20px;
        text-align: center;
        transition: transform 0.2s;
    }
    .kpi-card:hover { transform: translateY(-2px); }
    .kpi-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #7a8caa;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.6rem;
        font-weight: 600;
        color: #5ac8a0;
        line-height: 1.1;
    }
    .kpi-unit {
        font-size: 0.75rem;
        color: #5a7090;
        margin-top: 3px;
    }

    /* Feasibility badge */
    .badge-profit {
        display: inline-block;
        background: #1a3d2b;
        color: #4dda8a;
        border: 1px solid #2a6645;
        border-radius: 20px;
        padding: 6px 22px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.9rem;
        font-weight: 600;
        letter-spacing: 0.1em;
    }
    .badge-loss {
        display: inline-block;
        background: #3d1a1a;
        color: #ff6b6b;
        border: 1px solid #662a2a;
        border-radius: 20px;
        padding: 6px 22px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.9rem;
        font-weight: 600;
        letter-spacing: 0.1em;
    }

    /* Section headers */
    .section-header {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #5ac8a0;
        border-left: 3px solid #5ac8a0;
        padding-left: 10px;
        margin: 28px 0 12px 0;
    }

    /* Comparison delta */
    .delta-pos {
        color: #4dda8a;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 600;
    }
    .delta-neg {
        color: #ff6b6b;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 600;
    }

    /* Info boxes */
    .info-box {
        background: #161e30;
        border-left: 3px solid #3a5080;
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        font-size: 0.82rem;
        color: #8099bb;
        margin-bottom: 14px;
    }

    /* Divider */
    hr { border-color: #2a3145; }

    /* Streamlit element overrides */
    .stSlider label { color: #9ab0cc !important; font-size: 0.85rem; }
    .stCheckbox label { color: #9ab0cc !important; }
    h1 { color: #e0e6f0 !important; font-family: 'IBM Plex Sans', sans-serif !important; font-weight: 700 !important; }
    h2 { color: #ccd6e8 !important; font-family: 'IBM Plex Sans', sans-serif !important; }
    h3 { color: #a0b4cc !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PROCESS MODEL FUNCTIONS
# ─────────────────────────────────────────────

def get_yield(p2o5: float) -> float:
    """
    Returns TSP yield (%) based on P2O5 content in rock phosphate.
    Uses range-based lookup (engineering approximation).
    """
    if p2o5 <= 20:
        return 60.0
    elif p2o5 <= 25:
        return 70.0
    elif p2o5 <= 30:
        return 80.0
    else:
        return 90.0


def get_conversion(acid_conc: float) -> float:
    """
    Returns acid conversion (%) based on H2SO4 concentration.
    Higher acid concentration → better conversion of phosphate.
    """
    if acid_conc <= 90:
        return 65.0
    elif acid_conc <= 94:
        return 75.0
    elif acid_conc <= 96:
        return 85.0
    else:
        return 92.0


def compute_process(p2o5: float, feed_rate: float, acid_conc: float) -> dict:
    """
    Main process model: computes all production and economic outputs.

    Parameters:
        p2o5       : P2O5 content in rock phosphate (%)
        feed_rate  : Feed rate (tons/day)
        acid_conc  : H2SO4 concentration (%)

    Returns dict with all computed values.
    """
    # ── PROCESS OUTPUTS ──────────────────────────────────────
    yield_pct      = get_yield(p2o5)
    conversion_pct = get_conversion(acid_conc)

    tsp_per_day    = (yield_pct / 100) * feed_rate        # tons/day TSP
    gypsum_per_day = 0.80 * feed_rate                     # tons/day gypsum byproduct
    hf_per_day     = 0.02 * feed_rate                     # tons/day HF emission

    # Convert to annual (330 operating days/year is standard for chemical plants)
    op_days        = 330
    tsp_annual     = tsp_per_day    * op_days
    gypsum_annual  = gypsum_per_day * op_days
    hf_annual      = hf_per_day     * op_days

    # ── ECONOMICS ────────────────────────────────────────────

    # Raw material cost (annual)
    # Assuming local rock phosphate @ $60/ton + acid @ $150/ton feed
    # Acid usage estimated at ~0.6 tons H2SO4 per ton of rock feed (typical TSP stoichiometry)
    acid_usage_per_day = 0.60 * feed_rate                 # tons/day acid consumed
    raw_mat_annual = (
        feed_rate       * op_days * 60    +   # local rock phosphate
        acid_usage_per_day * op_days * 150    # sulfuric acid
    )

    # Utility cost = 15% of raw material cost (simplified lump sum)
    utility_cost = 0.15 * raw_mat_annual

    # Maintenance = 5% of raw material cost (O&M practice)
    maintenance_cost = 0.05 * raw_mat_annual

    # Total OPEX
    opex = raw_mat_annual + utility_cost + maintenance_cost

    # Revenue
    revenue = (tsp_annual * 600) + (gypsum_annual * 25)

    # Gross profit
    gross_profit = revenue - opex

    # Corporate tax (Pakistan: 29%)
    tax_rate = 0.29
    net_profit = gross_profit * (1 - tax_rate)

    # CAPEX using six-tenths rule: CAPEX = 50M × (feed/200)^0.6
    capex = 50_000_000 * ((feed_rate / 200) ** 0.6)

    # Payback period (years)
    payback = capex / net_profit if net_profit > 0 else float('inf')

    return {
        # Process
        "yield_pct"        : yield_pct,
        "conversion_pct"   : conversion_pct,
        "tsp_per_day"      : tsp_per_day,
        "gypsum_per_day"   : gypsum_per_day,
        "hf_per_day"       : hf_per_day,
        "tsp_annual"       : tsp_annual,
        "gypsum_annual"    : gypsum_annual,
        "hf_annual"        : hf_annual,
        # Economics
        "raw_mat_annual"   : raw_mat_annual,
        "utility_cost"     : utility_cost,
        "maintenance_cost" : maintenance_cost,
        "opex"             : opex,
        "revenue"          : revenue,
        "gross_profit"     : gross_profit,
        "net_profit"       : net_profit,
        "capex"            : capex,
        "payback"          : payback,
    }


# ─────────────────────────────────────────────
# PLOTLY THEME DEFAULTS
# ─────────────────────────────────────────────
CHART_BG    = "#0f1117"
PAPER_BG    = "#161b27"
GRID_COLOR  = "#1e2a40"
FONT_COLOR  = "#9ab0cc"
ACCENT1     = "#5ac8a0"   # teal-green
ACCENT2     = "#4a90d9"   # blue
ACCENT3     = "#e8944a"   # amber
ACCENT4     = "#a07ae0"   # purple

def base_layout(title: str = "") -> dict:
    return dict(
        title=dict(text=title, font=dict(size=13, color="#c0d0e8", family="IBM Plex Mono")),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=CHART_BG,
        font=dict(color=FONT_COLOR, family="IBM Plex Sans"),
        margin=dict(l=40, r=20, t=45, b=40),
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
    )


# ─────────────────────────────────────────────
# SIDEBAR — INPUTS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌱 TSP Dashboard")
    st.markdown("<div class='info-box'>Adjust process inputs below. Results update instantly.</div>",
                unsafe_allow_html=True)

    st.markdown("### Feed Parameters")
    p2o5 = st.slider(
        "P₂O₅ Content in Rock Phosphate (%)",
        min_value=15, max_value=35, value=25, step=1,
        help="Higher P₂O₅ grade → better yield"
    )
    feed_rate = st.slider(
        "Feed Rate (tons/day)",
        min_value=50, max_value=500, value=200, step=10,
        help="Daily throughput of rock phosphate"
    )

    st.markdown("### Acid Parameters")
    acid_conc = st.slider(
        "Acid Concentration (% H₂SO₄)",
        min_value=85, max_value=98, value=93, step=1,
        help="Higher concentration → better conversion efficiency"
    )

    st.markdown("### Mode")
    compare_mode = st.checkbox(
        "📊 Comparison Mode",
        help="Compare current settings with baseline case"
    )

    st.markdown("---")
    st.markdown("<div style='font-size:0.72rem; color:#4a6080; font-family: IBM Plex Mono;'>Operating days: 330/year<br>Tax rate: 29% (Pakistan)<br>Pricing: USD</div>",
                unsafe_allow_html=True)


# ─────────────────────────────────────────────
# COMPUTE CURRENT CASE
# ─────────────────────────────────────────────
res = compute_process(p2o5, feed_rate, acid_conc)

# Baseline (fixed reference case)
BASELINE = {"p2o5": 25, "feed_rate": 200, "acid_conc": 93}
base_res  = compute_process(**BASELINE)


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("# 🧪 Triple Super Phosphate (TSP) Production Dashboard")
st.markdown(
    "<div class='info-box'>Decision-support tool for TSP fertilizer production using rock phosphate and sulfuric acid. "
    "All outputs are engineering estimates based on numerical range models — not rigorous simulations.</div>",
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# FEASIBILITY BADGE
# ─────────────────────────────────────────────
col_f1, col_f2 = st.columns([1, 4])
with col_f1:
    if res["net_profit"] > 0:
        st.markdown("<div class='badge-profit'>✅ PROFITABLE</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='badge-loss'>❌ LOSS-MAKING</div>", unsafe_allow_html=True)
with col_f2:
    profit_fmt = f"${res['net_profit']/1e6:+.2f}M/yr net profit"
    st.markdown(f"<div style='color:#7a8caa; font-size:0.85rem; padding-top:8px;'>{profit_fmt}</div>",
                unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# KPI ROW
# ─────────────────────────────────────────────
st.markdown("<div class='section-header'>Key Performance Indicators</div>", unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)

kpi_data = [
    (k1, "TSP Yield",       f"{res['yield_pct']:.0f}%",             "based on P₂O₅ grade"),
    (k2, "Acid Conversion",  f"{res['conversion_pct']:.0f}%",       "based on H₂SO₄ conc."),
    (k3, "TSP Production",   f"{res['tsp_annual']:,.0f}",           "tons / year"),
    (k4, "Net Profit",       f"${res['net_profit']/1e6:.2f}M",      "USD / year (after tax)"),
    (k5, "Payback Period",
        f"{res['payback']:.1f} yr" if res['payback'] != float('inf') else "N/A",
        "CAPEX / Net Profit"),
]

for col, label, value, unit in kpi_data:
    with col:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>{label}</div>
            <div class='kpi-value'>{value}</div>
            <div class='kpi-unit'>{unit}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PRODUCTION SUMMARY TABLE
# ─────────────────────────────────────────────
st.markdown("<div class='section-header'>Production Summary</div>", unsafe_allow_html=True)

col_t1, col_t2, col_t3 = st.columns(3)
with col_t1:
    st.metric("TSP (tons/day)",    f"{res['tsp_per_day']:.1f}")
    st.metric("TSP (tons/year)",   f"{res['tsp_annual']:,.0f}")
with col_t2:
    st.metric("Gypsum (tons/day)", f"{res['gypsum_per_day']:.1f}")
    st.metric("Gypsum (tons/year)",f"{res['gypsum_annual']:,.0f}")
with col_t3:
    st.metric("HF (tons/day)",     f"{res['hf_per_day']:.2f}")
    st.metric("HF (tons/year)",    f"{res['hf_annual']:,.1f}")

st.markdown("---")

# ─────────────────────────────────────────────
# CHARTS — ROW 1
# ─────────────────────────────────────────────
st.markdown("<div class='section-header'>Process Analysis</div>", unsafe_allow_html=True)

chart_col1, chart_col2 = st.columns(2)

# ── Chart 1: P2O5 vs Yield (line graph) ──────
with chart_col1:
    st.markdown("**P₂O₅ Content vs TSP Yield**")
    st.markdown("<div class='info-box'>Shows how ore grade directly impacts yield. Higher-grade rock increases TSP recovery.</div>",
                unsafe_allow_html=True)

    p2o5_range  = list(range(15, 36))
    yield_range = [get_yield(v) for v in p2o5_range]

    fig_yield = go.Figure()
    fig_yield.add_trace(go.Scatter(
        x=p2o5_range, y=yield_range,
        mode="lines+markers",
        line=dict(color=ACCENT1, width=2.5),
        marker=dict(size=6, color=ACCENT1),
        fill="tozeroy",
        fillcolor="rgba(90,200,160,0.08)",
        name="Yield (%)"
    ))
    # Highlight current point
    fig_yield.add_trace(go.Scatter(
        x=[p2o5], y=[res["yield_pct"]],
        mode="markers",
        marker=dict(size=14, color=ACCENT3, symbol="diamond",
                    line=dict(width=2, color="#fff")),
        name="Current"
    ))
    fig_yield.update_layout(
        **base_layout(""),
        xaxis_title="P₂O₅ Content (%)",
        yaxis_title="Yield (%)",
        yaxis_range=[50, 100],
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        height=300,
    )
    st.plotly_chart(fig_yield, width='stretch')

# ── Chart 2: Acid Concentration vs Conversion ──
with chart_col2:
    st.markdown("**H₂SO₄ Concentration vs Conversion**")
    st.markdown("<div class='info-box'>More concentrated acid drives better phosphate conversion. Above 96% gives diminishing returns.</div>",
                unsafe_allow_html=True)

    acid_range = list(range(85, 99))
    conv_range = [get_conversion(v) for v in acid_range]

    fig_conv = go.Figure()
    fig_conv.add_trace(go.Scatter(
        x=acid_range, y=conv_range,
        mode="lines+markers",
        line=dict(color=ACCENT2, width=2.5),
        marker=dict(size=6, color=ACCENT2),
        fill="tozeroy",
        fillcolor="rgba(74,144,217,0.08)",
        name="Conversion (%)"
    ))
    fig_conv.add_trace(go.Scatter(
        x=[acid_conc], y=[res["conversion_pct"]],
        mode="markers",
        marker=dict(size=14, color=ACCENT3, symbol="diamond",
                    line=dict(width=2, color="#fff")),
        name="Current"
    ))
    fig_conv.update_layout(
        **base_layout(""),
        xaxis_title="H₂SO₄ Concentration (%)",
        yaxis_title="Conversion (%)",
        yaxis_range=[55, 100],
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        height=300,
    )
    st.plotly_chart(fig_conv, width='stretch')

st.markdown("---")

# ─────────────────────────────────────────────
# CHARTS — ROW 2
# ─────────────────────────────────────────────
st.markdown("<div class='section-header'>Economic Analysis</div>", unsafe_allow_html=True)

chart_col3, chart_col4 = st.columns([3, 2])

# ── Chart 3: Revenue vs OPEX vs Profit (bar) ──
with chart_col3:
    st.markdown("**Revenue · OPEX · Profit Breakdown (USD/year)**")
    st.markdown("<div class='info-box'>Revenue from TSP + gypsum sales. OPEX = raw materials + utilities + maintenance. Net profit is after 29% corporate tax.</div>",
                unsafe_allow_html=True)

    fig_econ = go.Figure()
    categories = ["Revenue", "OPEX", "Gross Profit", "Net Profit (After Tax)"]
    values = [
        res["revenue"],
        res["opex"],
        res["gross_profit"],
        res["net_profit"],
    ]
    colors = [ACCENT1, ACCENT3, ACCENT2, ACCENT4]

    fig_econ.add_trace(go.Bar(
        x=categories,
        y=[v / 1e6 for v in values],
        marker_color=colors,
        marker_line=dict(width=0),
        text=[f"${v/1e6:.2f}M" for v in values],
        textposition="outside",
        textfont=dict(color="#c0d0e8", size=11, family="IBM Plex Mono"),
    ))
    fig_econ.update_layout(
        **base_layout(""),
        yaxis_title="USD (Millions)",
        xaxis_tickfont=dict(size=11),
        height=340,
        showlegend=False,
    )
    st.plotly_chart(fig_econ, width='stretch')

# ── Chart 4: OPEX Pie breakdown ───────────────
with chart_col4:
    st.markdown("**OPEX Cost Breakdown**")
    st.markdown("<div class='info-box'>Raw materials dominate costs. Utilities (15%) and maintenance (5%) are proportional estimates.</div>",
                unsafe_allow_html=True)

    opex_labels  = ["Raw Materials", "Utilities (15%)", "Maintenance (5%)"]
    opex_values  = [res["raw_mat_annual"], res["utility_cost"], res["maintenance_cost"]]
    opex_colors  = [ACCENT3, ACCENT2, ACCENT4]

    fig_pie = go.Figure(go.Pie(
        labels=opex_labels,
        values=opex_values,
        hole=0.45,
        marker=dict(colors=opex_colors, line=dict(color="#0f1117", width=2)),
        textfont=dict(size=11, color="#e0e6f0"),
        hovertemplate="%{label}<br>$%{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    # Note: base_layout() already sets margin, so we override it via update_layout separately
    pie_layout = base_layout("")
    pie_layout["margin"] = dict(l=0, r=10, t=30, b=20)   # override the default margin
    fig_pie.update_layout(
        **pie_layout,
        height=340,
        showlegend=True,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=10),
            orientation="v",
            x=0.55, y=0.5,
        ),
    )
    st.plotly_chart(fig_pie, width='stretch')

st.markdown("---")

# ─────────────────────────────────────────────
# CAPEX SECTION
# ─────────────────────────────────────────────
st.markdown("<div class='section-header'>Capital Expenditure (CAPEX)</div>", unsafe_allow_html=True)
capex_col1, capex_col2, capex_col3 = st.columns(3)
with capex_col1:
    st.metric("Estimated CAPEX", f"${res['capex']/1e6:.2f}M USD",
              help="CAPEX = $50M × (Feed Rate / 200)^0.6")
with capex_col2:
    st.metric("Annual OPEX",     f"${res['opex']/1e6:.2f}M USD")
with capex_col3:
    pb = res['payback']
    st.metric("Simple Payback",
              f"{pb:.1f} years" if pb != float('inf') else "Not profitable",
              help="Payback = CAPEX / Net Annual Profit")

# CAPEX sensitivity: feed rate sweep
st.markdown("**CAPEX Sensitivity to Feed Rate**")
feed_sweep   = list(range(50, 510, 10))
capex_sweep  = [50e6 * (f / 200) ** 0.6 for f in feed_sweep]

fig_capex = go.Figure()
fig_capex.add_trace(go.Scatter(
    x=feed_sweep, y=[c / 1e6 for c in capex_sweep],
    mode="lines", line=dict(color=ACCENT4, width=2.5),
    fill="tozeroy", fillcolor="rgba(160,122,224,0.08)",
    name="CAPEX (M$)"
))
fig_capex.add_trace(go.Scatter(
    x=[feed_rate], y=[res["capex"] / 1e6],
    mode="markers",
    marker=dict(size=12, color=ACCENT3, symbol="diamond",
                line=dict(width=2, color="#fff")),
    name="Current"
))
fig_capex.update_layout(
    **base_layout(""),
    xaxis_title="Feed Rate (tons/day)",
    yaxis_title="CAPEX (Million USD)",
    height=260,
    showlegend=True,
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
)
st.plotly_chart(fig_capex, width='stretch')


# ─────────────────────────────────────────────
# COMPARISON MODE
# ─────────────────────────────────────────────
if compare_mode:
    st.markdown("---")
    st.markdown("<div class='section-header'>📊 Comparison Mode — Current vs Baseline</div>",
                unsafe_allow_html=True)
    st.markdown(
        f"<div class='info-box'>Baseline: P₂O₅ = {BASELINE['p2o5']}% | "
        f"Feed Rate = {BASELINE['feed_rate']} TPD | "
        f"Acid = {BASELINE['acid_conc']}% H₂SO₄</div>",
        unsafe_allow_html=True
    )

    # Delta calculations
    delta_profit = res["net_profit"]  - base_res["net_profit"]
    delta_yield  = res["yield_pct"]   - base_res["yield_pct"]
    delta_payback= res["payback"]     - base_res["payback"]
    delta_rev    = res["revenue"]     - base_res["revenue"]

    cmp1, cmp2, cmp3, cmp4 = st.columns(4)

    def delta_str(val, unit="", prefix="$", millions=False):
        if millions:
            v = val / 1e6
            s = f"+{prefix}{v:.2f}M{unit}" if v >= 0 else f"{prefix}{v:.2f}M{unit}"
        else:
            s = f"+{val:+.1f}{unit}" if val >= 0 else f"{val:+.1f}{unit}"
        css = "delta-pos" if val >= 0 else "delta-neg"
        return f"<span class='{css}'>{s}</span>"

    with cmp1:
        st.markdown("**Yield (%)**")
        st.markdown(f"Current: **{res['yield_pct']:.0f}%** | Baseline: **{base_res['yield_pct']:.0f}%**")
        st.markdown(f"Δ {delta_str(delta_yield, unit='%', prefix='')}", unsafe_allow_html=True)

    with cmp2:
        st.markdown("**Net Profit**")
        st.markdown(f"Current: **${res['net_profit']/1e6:.2f}M** | Baseline: **${base_res['net_profit']/1e6:.2f}M**")
        st.markdown(f"Δ {delta_str(delta_profit, millions=True)}", unsafe_allow_html=True)

    with cmp3:
        st.markdown("**Revenue**")
        st.markdown(f"Current: **${res['revenue']/1e6:.2f}M** | Baseline: **${base_res['revenue']/1e6:.2f}M**")
        st.markdown(f"Δ {delta_str(delta_rev, millions=True)}", unsafe_allow_html=True)

    with cmp4:
        st.markdown("**Payback Period**")
        pb_cur  = f"{res['payback']:.1f} yr"   if res['payback']      != float('inf') else "N/A"
        pb_base = f"{base_res['payback']:.1f} yr" if base_res['payback'] != float('inf') else "N/A"
        st.markdown(f"Current: **{pb_cur}** | Baseline: **{pb_base}**")
        if res['payback'] != float('inf') and base_res['payback'] != float('inf'):
            st.markdown(f"Δ {delta_str(-delta_payback, unit=' yr', prefix='')}", unsafe_allow_html=True)

    # Side-by-side bar chart comparison
    st.markdown("<br>**Side-by-Side Economic Comparison**", unsafe_allow_html=True)

    compare_cats = ["Revenue", "OPEX", "Net Profit"]
    current_vals = [res["revenue"]/1e6,     res["opex"]/1e6,     res["net_profit"]/1e6]
    baseline_vals= [base_res["revenue"]/1e6, base_res["opex"]/1e6, base_res["net_profit"]/1e6]

    fig_cmp = go.Figure()
    fig_cmp.add_trace(go.Bar(
        name="Current Case", x=compare_cats, y=current_vals,
        marker_color=ACCENT1,
        text=[f"${v:.2f}M" for v in current_vals],
        textposition="outside",
        textfont=dict(size=10, family="IBM Plex Mono"),
    ))
    fig_cmp.add_trace(go.Bar(
        name="Baseline", x=compare_cats, y=baseline_vals,
        marker_color=ACCENT2,
        text=[f"${v:.2f}M" for v in baseline_vals],
        textposition="outside",
        textfont=dict(size=10, family="IBM Plex Mono"),
    ))
    fig_cmp.update_layout(
        **base_layout(""),
        barmode="group",
        yaxis_title="USD (Millions)",
        height=340,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=12)),
    )
    st.plotly_chart(fig_cmp, width='stretch')


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#3a5070; font-family: IBM Plex Mono; font-size:0.7rem; padding:10px 0;'>"
    "TSP Production Dashboard · Final Year Project · Decision Support Tool · Not a rigorous simulation"
    "</div>",
    unsafe_allow_html=True
)