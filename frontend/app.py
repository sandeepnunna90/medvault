import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()


@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_ANON_KEY"],
    )


supabase = get_supabase_client()

if "user" not in st.session_state:
    st.session_state.user = None
if "access_token" not in st.session_state:
    st.session_state.access_token = None


def show_auth_page():
    st.title("MedVault")
    st.caption("Personal Health Records Platform")

    tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Log In"):
            try:
                response = supabase.auth.sign_in_with_password(
                    {"email": email, "password": password}
                )
                st.session_state.user = response.user
                st.session_state.access_token = response.session.access_token
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {e}")

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
    st.title("MedVault Dashboard")
    st.write(f"Welcome, {st.session_state.user.email}")
    st.info("Dashboard coming in Day 4.")

    if st.button("Log Out"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.session_state.access_token = None
        st.rerun()


if st.session_state.user:
    show_dashboard()
else:
    show_auth_page()
