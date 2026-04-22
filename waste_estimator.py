import streamlit as st
import pandas as pd
import math
from datetime import datetime

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ApartmentWaste.io",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

  /* Dark industrial background */
  .stApp { background-color: #0f1117; color: #e8e8e0; }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: #161b22;
    border-right: 1px solid #2a2f3a;
  }
  section[data-testid="stSidebar"] * { color: #c9d1d9 !important; }

  /* Metric cards */
  .metric-card {
    background: #161b22;
    border: 1px solid #2a2f3a;
    border-radius: 8px;
    padding: 20px 24px;
    position: relative;
    overflow: hidden;
  }
  .metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
  }
  .metric-card.green::before  { background: #39d353; }
  .metric-card.blue::before   { background: #58a6ff; }
  .metric-card.orange::before { background: #f0883e; }
  .metric-card.purple::before { background: #bc8cff; }

  .metric-label {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #8b949e;
    margin-bottom: 6px;
  }
  .metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 32px;
    font-weight: 700;
    color: #e8e8e0;
    line-height: 1.1;
  }
  .metric-sub {
    font-size: 12px;
    color: #6e7681;
    margin-top: 4px;
  }

  /* Section headers */
  .section-header {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #39d353;
    border-bottom: 1px solid #2a2f3a;
    padding-bottom: 8px;
    margin: 32px 0 16px;
  }

  /* Config cards */
  .config-card {
    background: #161b22;
    border: 1px solid #2a2f3a;
    border-radius: 8px;
    padding: 18px 20px;
    margin-bottom: 12px;
  }
  .config-title {
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    color: #58a6ff;
    margin-bottom: 10px;
    letter-spacing: 0.05em;
  }
  .bin-tag {
    display: inline-block;
    background: #1f2937;
    border: 1px solid #374151;
    border-radius: 4px;
    padding: 3px 9px;
    margin: 3px;
    font-size: 12px;
    font-family: 'Space Mono', monospace;
    color: #d1d5db;
  }
  .bin-tag.trash   { border-color: #f0883e; color: #f0883e; }
  .bin-tag.recycle { border-color: #58a6ff; color: #58a6ff; }
  .bin-tag.compost { border-color: #39d353; color: #39d353; }

  /* Warnings */
  .warn-red {
    background: #2d1515;
    border: 1px solid #f85149;
    border-left: 4px solid #f85149;
    border-radius: 6px;
    padding: 14px 18px;
    color: #f85149;
    font-size: 14px;
    margin: 10px 0;
    font-family: 'Space Mono', monospace;
  }
  .warn-green {
    background: #0d2116;
    border: 1px solid #39d353;
    border-left: 4px solid #39d353;
    border-radius: 6px;
    padding: 14px 18px;
    color: #39d353;
    font-size: 14px;
    margin: 10px 0;
    font-family: 'Space Mono', monospace;
  }

  /* Table */
  .styled-table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .styled-table th {
    background: #21262d;
    color: #8b949e;
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 10px 14px;
    text-align: left;
    border-bottom: 1px solid #2a2f3a;
  }
  .styled-table td {
    padding: 10px 14px;
    border-bottom: 1px solid #1c2128;
    color: #c9d1d9;
  }
  .styled-table tr:hover td { background: #1c2128; }

  /* Hero */
  .hero {
    background: linear-gradient(135deg, #161b22 0%, #0f1117 100%);
    border: 1px solid #2a2f3a;
    border-radius: 10px;
    padding: 28px 32px;
    margin-bottom: 24px;
  }
  .hero-title {
    font-family: 'Space Mono', monospace;
    font-size: 26px;
    font-weight: 700;
    color: #e8e8e0;
    margin: 0;
  }
  .hero-title span { color: #39d353; }
  .hero-sub { color: #6e7681; font-size: 14px; margin-top: 6px; }

  div[data-testid="stExpander"] {
    background: #161b22;
    border: 1px solid #2a2f3a;
    border-radius: 8px;
  }
  div[data-testid="stExpander"] summary { color: #8b949e !important; }
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
LBS_PER_PERSON_PER_DAY = 4.9
LBS_PER_CUBIC_YARD     = 250
TOTER_CY               = 0.47          # cubic yards per 96-gal cart
TOTER_FOOTPRINT_SQFT   = 3 * 2         # sq ft per toter

DUMPSTER_SIZES = [8, 6, 4, 2]          # cubic yards, largest first
DUMPSTER_DIMS  = {                     # (width_ft, depth_ft)
    8: (6, 6),
    6: (6, 5),
    4: (6, 4.5),
    2: (6, 3),
}

# ── Greedy Solver ──────────────────────────────────────────────────────────────
def greedy_dumpsters(volume_cy: float) -> list[tuple[int, int]]:
    """Return list of (size_yd, count) pairs using greedy largest-first."""
    remaining = volume_cy
    result = []
    for size in DUMPSTER_SIZES:
        if remaining <= 0:
            break
        count = int(remaining // size)
        if count > 0:
            result.append((size, count))
            remaining -= count * size
    if remaining > 0.001:          # fractional remainder → smallest bin
        result.append((2, 1))
    return result

def dumpster_footprint(config: list[tuple[int, int]]) -> float:
    return sum(DUMPSTER_DIMS[sz][0] * DUMPSTER_DIMS[sz][1] * cnt
               for sz, cnt in config)

def toter_count(volume_cy: float) -> int:
    return math.ceil(volume_cy / TOTER_CY)

# ── Sidebar Inputs ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")

    st.markdown("**🏢 Building**")
    num_units   = st.number_input("Number of Units",          min_value=1, value=100, step=1)
    ppl_per_unit = st.number_input("Avg. People per Unit",    min_value=1.0, value=2.5, step=0.5)
    num_locations = st.number_input("Number of Waste Locations", min_value=1, value=3, step=1)
    area_per_loc  = st.number_input("Available Area per Location (sq ft)",
                                    min_value=10, value=150, step=10)

    st.markdown("---")
    st.markdown("**♻️ Diversion Programs**")
    recycling_on = st.toggle("Offer Recycling?", value=True)
    recycling_rate = 0.30
    if recycling_on:
        recycling_rate = st.slider("Recycling Diversion Rate (%)", 5, 80, 30) / 100

    composting_on = st.toggle("Offer Composting?", value=False)
    composting_rate = 0.10
    if composting_on:
        composting_rate = st.slider("Composting Diversion Rate (%)", 5, 50, 10) / 100

    st.markdown("---")
    st.markdown("**🚛 Collection Frequency**")
    trash_pickups   = st.slider("Weekly Trash Pickups",          1, 7, 2)
    recycle_pickups = st.slider("Weekly Recycling/Compost Pickups", 1, 7, 1,
                                disabled=not (recycling_on or composting_on))

# ── Core Calculations ──────────────────────────────────────────────────────────
population = num_units * ppl_per_unit

total_lbs_per_week  = population * LBS_PER_PERSON_PER_DAY * 7
total_cy_per_week   = total_lbs_per_week / LBS_PER_CUBIC_YARD
total_tons_per_week = total_lbs_per_week / 2000

recycling_cy = total_cy_per_week * recycling_rate if recycling_on else 0.0
composting_cy = total_cy_per_week * composting_rate if composting_on else 0.0
trash_cy = total_cy_per_week - recycling_cy - composting_cy

# Per-cycle volumes (volume that must fit before next pickup)
trash_cy_per_cycle   = trash_cy / trash_pickups
recycle_cy_per_cycle = recycling_cy / recycle_pickups if recycling_on else 0
compost_cy_per_cycle = composting_cy / recycle_pickups if composting_on else 0

# Per-location volumes
trash_per_loc     = trash_cy_per_cycle / num_locations
recycle_per_loc   = recycle_cy_per_cycle / num_locations
compost_per_loc   = compost_cy_per_cycle / num_locations

# Bin configurations
trash_config  = greedy_dumpsters(trash_per_loc)
recycle_toters = toter_count(recycle_per_loc) if recycling_on else 0
compost_toters = toter_count(compost_per_loc) if composting_on else 0

# Capacity check
trash_cap_provided = sum(sz * cnt for sz, cnt in trash_config) * trash_pickups * num_locations
trash_required     = trash_cy
recycle_cap_provided = recycle_toters * TOTER_CY * recycle_pickups * num_locations if recycling_on else 0
recycle_required     = recycling_cy

compost_cap_provided = compost_toters * TOTER_CY * recycle_pickups * num_locations if composting_on else 0
compost_required     = composting_cy

# Footprint
trash_fp   = dumpster_footprint(trash_config)
recycle_fp = recycle_toters * TOTER_FOOTPRINT_SQFT
compost_fp = compost_toters * TOTER_FOOTPRINT_SQFT
total_fp   = trash_fp + recycle_fp + compost_fp
fp_exceeded = total_fp > area_per_loc

capacity_ok = (
    trash_cap_provided >= trash_required and
    (not recycling_on or recycle_cap_provided >= recycle_required) and
    (not composting_on or compost_cap_provided >= compost_required)
)

# ── Main Layout ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <p class="hero-title">Apartment<span>Waste</span> Estimator</p>
  <p class="hero-sub">EPA-standard waste modeling · Greedy bin optimization · Spatial constraint analysis</p>
</div>
""", unsafe_allow_html=True)

# ── KPI Row ────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="metric-card green">
      <div class="metric-label">Total Population</div>
      <div class="metric-value">{int(population):,}</div>
      <div class="metric-sub">{num_units} units × {ppl_per_unit} ppl</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card blue">
      <div class="metric-label">Weekly Tonnage</div>
      <div class="metric-value">{total_tons_per_week:.1f}</div>
      <div class="metric-sub">tons / week (all streams)</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card orange">
      <div class="metric-label">Total Weekly Volume</div>
      <div class="metric-value">{total_cy_per_week:.1f}</div>
      <div class="metric-sub">cubic yards / week</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card purple">
      <div class="metric-label">Waste Locations</div>
      <div class="metric-value">{num_locations}</div>
      <div class="metric-sub">{area_per_loc} sq ft each</div>
    </div>""", unsafe_allow_html=True)

# ── Volume Breakdown ───────────────────────────────────────────────────────────
st.markdown('<div class="section-header">// Volume Breakdown by Stream</div>', unsafe_allow_html=True)

streams = {
    "Stream": ["🗑️ Trash", "♻️ Recycling", "🌱 Composting", "— Total"],
    "Weekly Volume (cy)": [
        f"{trash_cy:.2f}",
        f"{recycling_cy:.2f}" if recycling_on else "—",
        f"{composting_cy:.2f}" if composting_on else "—",
        f"{total_cy_per_week:.2f}",
    ],
    "Weekly Weight (lbs)": [
        f"{trash_cy * LBS_PER_CUBIC_YARD:,.0f}",
        f"{recycling_cy * LBS_PER_CUBIC_YARD:,.0f}" if recycling_on else "—",
        f"{composting_cy * LBS_PER_CUBIC_YARD:,.0f}" if composting_on else "—",
        f"{total_lbs_per_week:,.0f}",
    ],
    "Diversion Rate": [
        f"{(1 - recycling_rate*(recycling_on) - composting_rate*(composting_on))*100:.0f}% of total",
        f"{recycling_rate*100:.0f}% of total" if recycling_on else "—",
        f"{composting_rate*100:.0f}% of total" if composting_on else "—",
        "100%",
    ],
}

df = pd.DataFrame(streams)
rows_html = "".join(
    f"<tr>{''.join(f'<td>{v}</td>' for v in row)}</tr>"
    for row in df.values
)
headers_html = "".join(f"<th>{h}</th>" for h in df.columns)
st.markdown(f"""
<table class="styled-table">
  <thead><tr>{headers_html}</tr></thead>
  <tbody>{rows_html}</tbody>
</table>
""", unsafe_allow_html=True)

# ── Site Configuration ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">// Site Configuration — Per Location</div>', unsafe_allow_html=True)

def fmt_dumpster_list(config):
    parts = []
    for sz, cnt in config:
        w, d = DUMPSTER_DIMS[sz]
        parts.append(f"<span class='bin-tag trash'>{cnt}× {sz}yd dumpster ({w}'×{d}')</span>")
    return " ".join(parts) if parts else "<span class='bin-tag'>none</span>"

trash_bins_html   = fmt_dumpster_list(trash_config)
recycle_bins_html = (f"<span class='bin-tag recycle'>{recycle_toters}× 96-gal Toter (3'×2')</span>"
                     if recycling_on and recycle_toters > 0
                     else "<span class='bin-tag'>not active</span>")
compost_bins_html = (f"<span class='bin-tag compost'>{compost_toters}× 96-gal Toter (3'×2')</span>"
                     if composting_on and compost_toters > 0
                     else "<span class='bin-tag'>not active</span>")

fp_color = "#f85149" if fp_exceeded else "#39d353"

st.markdown(f"""
<div class="config-card">
  <div class="config-title">📍 Each of the {num_locations} Waste Stations — Identical Configuration</div>
  <p style="font-size:13px; color:#8b949e; margin:0 0 8px;">🗑️ Trash Dumpsters</p>
  {trash_bins_html}
  <p style="font-size:13px; color:#8b949e; margin:12px 0 8px;">♻️ Recycling Carts</p>
  {recycle_bins_html}
  <p style="font-size:13px; color:#8b949e; margin:12px 0 8px;">🌱 Compost Carts</p>
  {compost_bins_html}
  <hr style="border-color:#2a2f3a; margin:14px 0 10px;">
  <span style="font-family:'Space Mono',monospace; font-size:12px; color:{fp_color};">
    Total Footprint: {total_fp:.1f} sq ft &nbsp;/&nbsp; Available: {area_per_loc} sq ft
  </span>
</div>
""", unsafe_allow_html=True)

# ── Warnings ───────────────────────────────────────────────────────────────────
if fp_exceeded:
    st.markdown(f"""
    <div class="warn-red">⚠️ SPATIAL CONSTRAINT EXCEEDED — Station footprint ({total_fp:.1f} sq ft)
    exceeds available area ({area_per_loc} sq ft) by {total_fp - area_per_loc:.1f} sq ft.
    Consider adding more locations, using smaller bins, or increasing pickup frequency.</div>
    """, unsafe_allow_html=True)

if not capacity_ok:
    deficits = []
    if trash_cap_provided < trash_required:
        deficits.append(f"Trash: need {trash_required:.1f} cy/wk, providing {trash_cap_provided:.1f} cy/wk")
    if recycling_on and recycle_cap_provided < recycle_required:
        deficits.append(f"Recycling: need {recycle_required:.1f} cy/wk, providing {recycle_cap_provided:.1f} cy/wk")
    if composting_on and compost_cap_provided < compost_required:
        deficits.append(f"Composting: need {compost_required:.1f} cy/wk, providing {compost_cap_provided:.1f} cy/wk")
    st.markdown(f"""
    <div class="warn-red">⚠️ CAPACITY DEFICIT — Increase pickup frequency or add more locations.<br>
    {"<br>".join(deficits)}</div>
    """, unsafe_allow_html=True)

if not fp_exceeded and capacity_ok:
    st.markdown("""
    <div class="warn-green">✅ ALL CHECKS PASSED — Configuration meets capacity and spatial requirements.</div>
    """, unsafe_allow_html=True)

# ── Detailed Capacity Table ────────────────────────────────────────────────────
st.markdown('<div class="section-header">// Capacity Verification</div>', unsafe_allow_html=True)

cap_rows = [
    ["🗑️ Trash",
     f"{trash_required:.2f} cy/wk",
     f"{trash_cap_provided:.2f} cy/wk",
     "✅ OK" if trash_cap_provided >= trash_required else "❌ DEFICIT"],
]
if recycling_on:
    cap_rows.append(["♻️ Recycling",
                     f"{recycle_required:.2f} cy/wk",
                     f"{recycle_cap_provided:.2f} cy/wk",
                     "✅ OK" if recycle_cap_provided >= recycle_required else "❌ DEFICIT"])
if composting_on:
    cap_rows.append(["🌱 Composting",
                     f"{compost_required:.2f} cy/wk",
                     f"{compost_cap_provided:.2f} cy/wk",
                     "✅ OK" if compost_cap_provided >= compost_required else "❌ DEFICIT"])

cap_html = "".join(
    f"<tr>{''.join(f'<td>{v}</td>' for v in r)}</tr>"
    for r in cap_rows
)
st.markdown(f"""
<table class="styled-table">
  <thead><tr>
    <th>Stream</th><th>Required (weekly)</th>
    <th>Provided (weekly)</th><th>Status</th>
  </tr></thead>
  <tbody>{cap_html}</tbody>
</table>
""", unsafe_allow_html=True)

# ── Methodology ───────────────────────────────────────────────────────────────
with st.expander("📖 Methodology & Assumptions"):
    st.markdown("""
**Generation Rate** — The EPA's 2021 *Advancing Sustainable Materials Management* report
establishes **4.9 lbs per person per day** as the national residential solid waste generation
baseline. This figure includes all material before diversion (recycling/composting).

**Density Conversion** — Loose residential MSW is assumed at **250 lbs per cubic yard**,
a standard engineering value for uncompacted material in roll-out or front-load receptacles.
This converts weight-based estimates to volumetric bin sizing.

**Diversion Logic** — Recycling and composting rates are applied to the **total waste pool**.
The remaining fraction becomes the trash stream. Volumes are calculated as:
- `Trash (cy/wk) = Total (cy/wk) × (1 − recycling_rate − composting_rate)`
- `Recycling (cy/wk) = Total (cy/wk) × recycling_rate`
- `Composting (cy/wk) = Total (cy/wk) × composting_rate`

**Greedy Bin Algorithm** — For each trash station, the required per-cycle volume
is computed as `Total Trash ÷ (Locations × Pickups/week)`. The solver fills that
volume greedily using the largest available dumpster (8 yd³), then fills remainders
with progressively smaller units (6, 4, 2 yd³).

**Recycling/Compost Carts** — 96-gallon "Toter" carts (≈ 0.47 yd³ each, 3′ × 2′ footprint)
are sized using `ceil(volume / 0.47)`.

**Spatial Check** — Footprint = sum of all bin footprints at one station.
Flagged if footprint > user-specified available area per station.
    """)

# ── Download Report ────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">// Export</div>', unsafe_allow_html=True)

def build_report():
    lines = [
        "=" * 60,
        "  APARTMENT WASTE ESTIMATOR — CONFIGURATION REPORT",
        f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "=" * 60,
        "",
        "── INPUTS ─────────────────────────────────────────────",
        f"  Units:                    {num_units}",
        f"  Avg people/unit:          {ppl_per_unit}",
        f"  Total population:         {int(population)}",
        f"  Waste locations:          {num_locations}",
        f"  Area per location:        {area_per_loc} sq ft",
        f"  Recycling:                {'ON (' + str(int(recycling_rate*100)) + '%)' if recycling_on else 'OFF'}",
        f"  Composting:               {'ON (' + str(int(composting_rate*100)) + '%)' if composting_on else 'OFF'}",
        f"  Trash pickups/week:       {trash_pickups}",
        f"  Recycling pickups/week:   {recycle_pickups}",
        "",
        "── VOLUME SUMMARY ─────────────────────────────────────",
        f"  Total weekly generation:  {total_cy_per_week:.2f} cy  ({total_tons_per_week:.2f} tons)",
        f"  Trash stream:             {trash_cy:.2f} cy/wk",
        f"  Recycling stream:         {recycling_cy:.2f} cy/wk" if recycling_on else "  Recycling stream:         N/A",
        f"  Composting stream:        {composting_cy:.2f} cy/wk" if composting_on else "  Composting stream:        N/A",
        "",
        "── PER-LOCATION CONFIGURATION ─────────────────────────",
    ]
    for sz, cnt in trash_config:
        w, d = DUMPSTER_DIMS[sz]
        lines.append(f"  Trash:      {cnt}× {sz}-yd dumpster  ({w}' × {d}')")
    if recycling_on:
        lines.append(f"  Recycling:  {recycle_toters}× 96-gal Toter  (3' × 2')")
    if composting_on:
        lines.append(f"  Composting: {compost_toters}× 96-gal Toter  (3' × 2')")
    lines += [
        f"  Total footprint: {total_fp:.1f} sq ft  ({'EXCEEDS' if fp_exceeded else 'within'} {area_per_loc} sq ft limit)",
        "",
        "── STATUS ──────────────────────────────────────────────",
        f"  Spatial constraint:  {'⚠ EXCEEDED' if fp_exceeded else '✓ OK'}",
        f"  Capacity check:      {'⚠ DEFICIT' if not capacity_ok else '✓ OK'}",
        "",
        "── METHODOLOGY ─────────────────────────────────────────",
        "  Generation: 4.9 lbs/person/day (EPA 2021)",
        "  Density:    250 lbs/cubic yard (residential MSW)",
        "  Algorithm:  Greedy largest-first bin packing",
        "=" * 60,
    ]
    return "\n".join(lines)

report_text = build_report()
st.download_button(
    label="⬇ Download Configuration Report (.txt)",
    data=report_text,
    file_name=f"waste_config_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
    mime="text/plain",
)
