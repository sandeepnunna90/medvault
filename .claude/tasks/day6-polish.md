# Day 6: Polish — Delete Reports + Session Persistence + Google OAuth

## Context
Day 5 left three deferred items: users can't delete reports, refreshing the page logs them out, and login is email-only. Day 6 addresses all three.

---

## Feature 1: Delete Reports

**Problem:** Failed/duplicate/unwanted reports accumulate in the Review dropdown with no way to remove them.

**Backend — add DELETE endpoint** (`backend/routers/reports.py`):
- `DELETE /reports/{report_id}`
- Verify JWT token (reuse existing `verify_token()`)
- Verify the report belongs to the requesting user (query reports table with user_id filter)
- Delete file from Supabase Storage (`supabase.storage.from_("reports").remove([storage_path])`)
- Delete report row — lab_results cascade automatically via FK `ON DELETE CASCADE`

**Frontend — add delete button** (`frontend/pages/review.py`):
- Add a "Delete this report" button below the report selector
- Show `st.warning` confirmation prompt with a confirm button (two-step: click delete → confirm)
- On confirm: call `DELETE /reports/{report_id}` with Bearer token
- On success: `st.rerun()` to refresh the page

---

## Feature 2: Session Persistence on Refresh

**Problem:** Streamlit's `session_state` is in-memory only — refreshing the page clears it and logs the user out.

**Approach:** Use `extra-streamlit-components` CookieManager to store the access token in a browser cookie.

**Changes to `frontend/app.py`**:
1. Install `extra-streamlit-components` (add to `requirements.txt`)
2. On successful login: write `access_token` and `user_email` to a cookie (7-day expiry)
3. On app load (before showing login form): check for cookie → if found, restore session state silently
4. On logout: clear the cookie

---

## Feature 3: Google OAuth

**Problem:** Email/password only. Supabase supports Google OAuth but Streamlit can't handle redirects natively.

**Approach:** Supabase OAuth URL → open in browser → redirect back with token in query params → capture in Streamlit.

**Changes to `frontend/app.py`**:
1. Add "Continue with Google" button that generates a Supabase OAuth URL (`supabase.auth.sign_in_with_oauth`)
2. Open the URL via `st.markdown` with a link (user clicks → browser redirect)
3. Supabase redirects back to the Streamlit app URL with `access_token` in the URL fragment/query params
4. On load, check `st.query_params` for `access_token` — if found, restore session and clear params

> Note: Streamlit Cloud URL fragments aren't accessible server-side. We'll use Supabase's `implicit` flow with query params, or configure redirect to a dedicated `/callback` Streamlit page.

---

## Files to Modify
- `backend/routers/reports.py` — add DELETE endpoint
- `frontend/pages/review.py` — add delete button + confirm flow
- `frontend/app.py` — session persistence + Google OAuth
- `requirements.txt` — add `extra-streamlit-components`

## Verification
1. Upload a report → delete it from Review page → confirm it disappears + storage file gone
2. Log in → refresh the page → confirm still logged in
3. Click "Continue with Google" → complete OAuth → confirm logged in with Google account
