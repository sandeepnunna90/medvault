import streamlit as st
from supabase import create_client
from streamlit_cookies_controller import CookieController

COOKIE_NAME = "medvault_token"


def get_controller():
    if "cookie_controller" not in st.session_state:
        st.session_state.cookie_controller = CookieController()
    return st.session_state.cookie_controller


def restore_session():
    """Restore session from cookie if not already in session_state.
    Returns True if authenticated, False otherwise.
    """
    if "user" not in st.session_state:
        st.session_state.user = None
    if "access_token" not in st.session_state:
        st.session_state.access_token = None

    if not st.session_state.user:
        token = get_controller().get(COOKIE_NAME)
        if token:
            try:
                supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])
                user_response = supabase.auth.get_user(token)
                st.session_state.user = user_response.user
                st.session_state.access_token = token
            except Exception:
                get_controller().remove(COOKIE_NAME)

    return bool(st.session_state.user)
