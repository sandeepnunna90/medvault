import streamlit as st
from supabase import create_client
import pandas as pd
import requests
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from auth import restore_session

st.set_page_config(page_title="Review Results", page_icon="🔬")

if not restore_session():
    st.warning("Please log in first.")
    st.stop()

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])
supabase.postgrest.auth(st.session_state.access_token)


def get_status(row: dict) -> str:
    try:
        value = float(row["value"])
        low = row.get("reference_range_low")
        high = row.get("reference_range_high")
        if low is not None and value < float(low):
            return "Low"
        if high is not None and value > float(high):
            return "High"
        return "Normal"
    except (TypeError, ValueError):
        return "—"


def highlight_status(val: str) -> str:
    colors = {"High": "color: red", "Low": "color: orange", "Normal": "color: green"}
    return colors.get(val, "")


st.title("Lab Results Review")

# Fetch reports for this user
reports_resp = (
    supabase.table("reports")
    .select("id, file_name, uploaded_at, status")
    .eq("user_id", st.session_state.user.id)
    .order("uploaded_at", desc=True)
    .execute()
)
reports = reports_resp.data

if not reports:
    st.info("No reports yet. Upload a lab report first.")
    st.stop()

# Report selector — use full timestamp to avoid key collisions
report_options = {
    f"{r['file_name']} — {r['uploaded_at'][:16].replace('T', ' ')}": r["id"]
    for r in reports
}
selected_label = st.selectbox("Select report", list(report_options.keys()))
report_id = report_options[selected_label]

# Delete report
with st.expander("Danger zone"):
    st.warning("Deleting this report will permanently remove it and all extracted results.")
    if st.button("Delete this report", type="primary"):
        st.session_state["confirm_delete"] = report_id

if st.session_state.get("confirm_delete") == report_id:
    st.error(f"Are you sure you want to delete **{selected_label}**?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, delete it"):
            backend_url = st.secrets.get("BACKEND_URL", "http://localhost:8000")
            resp = requests.delete(
                f"{backend_url}/reports/{report_id}",
                headers={"Authorization": f"Bearer {st.session_state.access_token}"},
            )
            if resp.status_code == 200:
                st.session_state.pop("confirm_delete", None)
                st.success("Report deleted.")
                st.rerun()
            else:
                st.error(f"Failed to delete: {resp.text}")
    with col2:
        if st.button("Cancel"):
            st.session_state.pop("confirm_delete", None)
            st.rerun()

# Fetch lab results for selected report
results_resp = (
    supabase.table("lab_results")
    .select("test_name, value, unit, reference_range_low, reference_range_high, category, date, lab_source, confidence")
    .eq("report_id", report_id)
    .order("category")
    .execute()
)
results = results_resp.data

if not results:
    st.warning("No extracted results for this report. It may still be processing or extraction failed.")
    st.stop()

# Build dataframe
df = pd.DataFrame(results)
df["status"] = df.apply(get_status, axis=1)
df["reference_range"] = df.apply(
    lambda r: f"{r['reference_range_low']} – {r['reference_range_high']}"
    if r["reference_range_low"] is not None and r["reference_range_high"] is not None
    else "—",
    axis=1,
)

display_df = df[[
    "test_name", "value", "unit", "reference_range", "status", "category", "confidence"
]].rename(columns={
    "test_name": "Test",
    "value": "Result",
    "unit": "Unit",
    "reference_range": "Reference Range",
    "status": "Status",
    "category": "Category",
    "confidence": "Confidence %",
})

st.dataframe(
    display_df.style.map(highlight_status, subset=["Status"]),
    width="stretch",
    hide_index=True,
)

st.caption(f"{len(results)} test(s) extracted · Lab: {results[0].get('lab_source') or 'Unknown'} · Date: {results[0].get('date') or 'Unknown'}")
