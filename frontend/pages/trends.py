import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import pandas as pd
import plotly.graph_objects as go
import os

load_dotenv()

st.set_page_config(page_title="Trends", page_icon="📈")

if not st.session_state.get("user") or not st.session_state.get("access_token"):
    st.warning("Please log in first.")
    st.stop()

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])
supabase.postgrest.auth(st.session_state.access_token)

# Fetch all lab results
results_resp = (
    supabase.table("lab_results")
    .select("test_name, value, unit, reference_range_low, reference_range_high, category, date, uploaded_at")
    .eq("user_id", st.session_state.user.id)
    .execute()
)
all_data = results_resp.data or []

if not all_data:
    st.info("No lab results yet. Upload a report first.")
    st.stop()

df = pd.DataFrame(all_data)

# Resolve effective date: use report date if available, else upload date
def resolve_date(row):
    if row["date"]:
        return row["date"]
    if row["uploaded_at"]:
        return row["uploaded_at"][:10]
    return None

df["effective_date"] = pd.to_datetime(df.apply(resolve_date, axis=1), errors="coerce")
df = df[df["effective_date"].notna()]

# Keep only numeric values
df["numeric_value"] = pd.to_numeric(df["value"], errors="coerce")
df = df[df["numeric_value"].notna()]

if df.empty:
    st.info("No numeric test results found.")
    st.stop()

st.title("Trends")

# Category selector — pre-select if navigated from dashboard
categories = sorted(df["category"].unique().tolist())
default_category = st.session_state.pop("selected_category", None)
default_index = categories.index(default_category) if default_category in categories else 0
selected_category = st.selectbox("Category", categories, index=default_index)

# Test name selector
cat_df = df[df["category"] == selected_category]
test_names = sorted(cat_df["test_name"].unique().tolist())

if not test_names:
    st.info(f"No numeric results for {selected_category}.")
    st.stop()

selected_test = st.selectbox("Test", test_names)

# Filter to selected test, sorted by date
test_df = cat_df[cat_df["test_name"] == selected_test].sort_values("effective_date").copy()

if test_df.empty:
    st.info("No data for this test.")
    st.stop()

# Determine reference range (most common non-null values)
ref_low_series = test_df["reference_range_low"].dropna()
ref_high_series = test_df["reference_range_high"].dropna()
has_ref = len(ref_low_series) > 0 and len(ref_high_series) > 0
ref_low_val = float(ref_low_series.mode().iloc[0]) if has_ref else None
ref_high_val = float(ref_high_series.mode().iloc[0]) if has_ref else None

# Color-code each data point
def point_color(value):
    if has_ref:
        if ref_low_val is not None and value < ref_low_val:
            return "orange"
        if ref_high_val is not None and value > ref_high_val:
            return "red"
    return "green"

test_df["color"] = test_df["numeric_value"].apply(point_color)

unit_label = test_df["unit"].dropna().iloc[0] if test_df["unit"].notna().any() else ""

# Build Plotly chart
fig = go.Figure()

# 1. Reference range shaded band
if has_ref:
    # Pad x range so band is visible even with 1 data point
    x_min = test_df["effective_date"].min() - pd.Timedelta(days=30)
    x_max = test_df["effective_date"].max() + pd.Timedelta(days=30)
    x_dates = [x_min, x_max]
    fig.add_trace(go.Scatter(
        x=x_dates + x_dates[::-1],
        y=[ref_high_val, ref_high_val, ref_low_val, ref_low_val],
        fill="toself",
        fillcolor="rgba(30, 120, 220, 0.08)",
        mode="lines",
        line=dict(width=0),
        hoverinfo="skip",
        showlegend=False,
    ))
    fig.add_hline(
        y=ref_high_val,
        line_dash="dash",
        line_color="steelblue",
        annotation_text=f"High: {ref_high_val}",
        annotation_position="top right",
    )
    fig.add_hline(
        y=ref_low_val,
        line_dash="dash",
        line_color="steelblue",
        annotation_text=f"Low: {ref_low_val}",
        annotation_position="bottom right",
    )

# 2. Line connecting points (only if 2+)
if len(test_df) > 1:
    fig.add_trace(go.Scatter(
        x=test_df["effective_date"],
        y=test_df["numeric_value"],
        mode="lines",
        line=dict(color="steelblue", width=2),
        hoverinfo="skip",
        showlegend=False,
    ))

# 3. Color-coded scatter points with hover
fig.add_trace(go.Scatter(
    x=test_df["effective_date"],
    y=test_df["numeric_value"],
    mode="markers",
    marker=dict(color=test_df["color"], size=10, line=dict(width=1, color="white")),
    text=test_df.apply(
        lambda r: f"{r['numeric_value']} {unit_label} ({r['color'].capitalize()})", axis=1
    ),
    hovertemplate="%{x|%Y-%m-%d}<br>%{text}<extra></extra>",
    showlegend=False,
))

fig.update_layout(
    title=f"{selected_test} over time",
    xaxis_title="Date",
    yaxis_title=unit_label,
    hovermode="x unified",
    plot_bgcolor="white",
    height=420,
    margin=dict(l=40, r=40, t=50, b=40),
)
fig.update_xaxes(showgrid=True, gridcolor="rgba(200,200,200,0.4)", tickformat="%b %d, %Y")
fig.update_yaxes(showgrid=True, gridcolor="rgba(200,200,200,0.4)")

st.plotly_chart(fig, width="stretch")

date_source = "report date" if test_df["date"].notna().any() else "upload date"
st.caption(f"{len(test_df)} data point(s) · X-axis uses {date_source} · Unit: {unit_label or '—'}")
