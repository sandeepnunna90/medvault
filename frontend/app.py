import streamlit as st
from supabase import create_client, Client
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(__file__))
from auth import restore_session, get_controller, COOKIE_NAME


def get_status(row) -> str:
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


@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_ANON_KEY"],
    )


supabase = get_supabase_client()
restore_session()


def show_auth_page():
    st.title("MedVault")
    st.caption("Personal Health Records Platform")

    tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])

    # Handle Google OAuth callback (access_token in query params)
    if "access_token" in st.query_params:
        token = st.query_params["access_token"]
        try:
            user_response = supabase.auth.get_user(token)
            st.session_state.user = user_response.user
            st.session_state.access_token = token
            get_controller().set(COOKIE_NAME, token, max_age=604800)
            st.query_params.clear()
            st.rerun()
        except Exception:
            st.error("Google login failed. Please try again.")

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Log In"):
            with st.spinner("Logging in..."):
                try:
                    response = supabase.auth.sign_in_with_password(
                        {"email": email, "password": password}
                    )
                    st.session_state.user = response.user
                    st.session_state.access_token = response.session.access_token
                    get_controller().set(COOKIE_NAME, response.session.access_token, max_age=604800)
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {e}")

        # TODO: Enable Google OAuth once configured in Supabase dashboard
        # st.divider()
        # oauth_resp = supabase.auth.sign_in_with_oauth({"provider": "google", ...})
        # st.link_button("Continue with Google", oauth_resp.url)

    with tab_signup:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Sign Up"):
            try:
                supabase.auth.sign_up({"email": email, "password": password})
                st.success("Account created! Check your email to confirm, then log in.")
            except Exception as e:
                st.error(f"Sign-up failed: {e}")


def show_dashboard():
    supabase.postgrest.auth(st.session_state.access_token)

    st.title("MedVault Dashboard")
    st.write(f"Welcome, {st.session_state.user.email}")

    reports_resp = (
        supabase.table("reports")
        .select("id", count="exact")
        .eq("user_id", st.session_state.user.id)
        .execute()
    )
    total_reports = reports_resp.count or 0

    results_resp = (
        supabase.table("lab_results")
        .select("test_name, value, unit, reference_range_low, reference_range_high, category, date, lab_source")
        .eq("user_id", st.session_state.user.id)
        .order("date", desc=True)
        .execute()
    )
    results_data = results_resp.data or []
    df = pd.DataFrame(results_data) if results_data else pd.DataFrame()

    col1, col2, col3 = st.columns(3)
    col1.metric("Reports Uploaded", total_reports)
    col2.metric("Tests Extracted", len(results_data))
    col3.metric("Categories", df["category"].nunique() if not df.empty else 0)

    st.divider()

    if df.empty:
        st.info("No lab results yet. Upload a report to see your health summary.")
    else:
        df["status"] = df.apply(get_status, axis=1)
        df["reference_range"] = df.apply(
            lambda r: f"{r['reference_range_low']} – {r['reference_range_high']}"
            if r["reference_range_low"] is not None and r["reference_range_high"] is not None
            else "—",
            axis=1,
        )

        for category in sorted(df["category"].unique()):
            cat_df = df[df["category"] == category]
            with st.expander(f"**{category}** — {len(cat_df)} test(s)", expanded=True):
                display_df = cat_df[["test_name", "value", "unit", "reference_range", "status", "date"]].rename(
                    columns={
                        "test_name": "Test",
                        "value": "Result",
                        "unit": "Unit",
                        "reference_range": "Reference Range",
                        "status": "Status",
                        "date": "Date",
                    }
                )
                st.dataframe(
                    display_df.style.map(highlight_status, subset=["Status"]),
                    width="stretch",
                    hide_index=True,
                )
                if st.button("📈 Trends", key=f"trends_{category}"):
                    st.session_state["selected_category"] = category
                    st.switch_page("pages/trends.py")

    st.divider()

    if st.button("Log Out"):
        supabase.auth.sign_out()
        get_controller().remove(COOKIE_NAME)
        st.session_state.user = None
        st.session_state.access_token = None
        st.rerun()


if st.session_state.get("user"):
    show_dashboard()
else:
    show_auth_page()
