import streamlit as st
import streamlit.components.v1 as stc
from supabase import create_client

COOKIE_NAME = "medvault_token"


def set_cookie(token: str) -> None:
    """Set the auth cookie via inline JS.

    Streamlit component iframes have allow-same-origin, so document.cookie
    sets a cookie for localhost:8501 that st.context.cookies can read on the
    next HTTP request (i.e. any sub-page refresh).
    """
    stc.html(
        f'<script>document.cookie = "{COOKIE_NAME}={token}; path=/; max-age=604800; SameSite=Lax";</script>',
        height=0,
    )


def remove_cookie() -> None:
    """Remove the auth cookie via inline JS."""
    stc.html(
        f'<script>document.cookie = "{COOKIE_NAME}=; path=/; max-age=0; SameSite=Lax";</script>',
        height=0,
    )


def restore_session() -> bool:
    """Restore session from cookie. Returns True if authenticated.

    Uses st.context.cookies — reads directly from the HTTP request headers,
    synchronous, no JS component timing issues on sub-page refresh.

    Skips cookie check if the user explicitly logged out in this session to
    prevent re-auth from a stale st.context.cookies value (which is frozen at
    WebSocket connection time and may still hold the old token).
    """
    if "user" not in st.session_state:
        st.session_state.user = None
    if "access_token" not in st.session_state:
        st.session_state.access_token = None

    if not st.session_state.user and not st.session_state.get("_logged_out"):
        token = st.context.cookies.get(COOKIE_NAME)
        if token:
            try:
                supabase = create_client(
                    st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"]
                )
                user_response = supabase.auth.get_user(token)
                st.session_state.user = user_response.user
                st.session_state.access_token = token
            except Exception:
                pass

    return bool(st.session_state.user)
