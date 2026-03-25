# Day 4: Dashboard + Category Detail Page

**Goal:** Replace the placeholder dashboard with real summary stats and category cards. Add a category detail page showing all tests for a selected category across all reports.

## New Files
```
frontend/
  pages/category.py    (new: category detail view)
```

## Modified Files
- `frontend/app.py` — replace show_dashboard() with real summary + category cards

## No backend changes needed
All data already exists in `lab_results`. Queries run directly from Streamlit using anon key + JWT. No new migrations or FastAPI endpoints.

## Steps
- [x] 1. Built `frontend/pages/category.py` initially — later removed (dashboard covers everything)
- [x] 2. Update `show_dashboard()` in `frontend/app.py` — summary metrics + expandable category sections
- [x] 3. Tested locally — dashboard shows metrics, category expanders with color-coded tables
- [x] 4. Commit + push

## Completed Notes
- Switched from category card grid → category detail page navigation to a single dashboard with expandable sections per category (Option A)
- category.py was built then removed — dashboard renders all categories inline
- All lab_results queried directly from Streamlit using anon key + JWT (no new backend endpoints)
- `get_status` and `highlight_status` helpers added to app.py

## Dashboard Design (`app.py`)

**Summary row** — 3 `st.metric()` in `st.columns(3)`:
- Reports Uploaded
- Tests Extracted
- Categories

**Category card grid** — 3-column layout, one button per category with data:
- Label: `{category}\n{count} test(s)`
- Click: sets `st.session_state["selected_category"]`, calls `st.switch_page("pages/category.py")`
- Sorted alphabetically

**Empty state:** `st.info()` if no lab results yet.

## Category Detail Design (`pages/category.py`)

- Back button at top → `st.switch_page("app.py")`
- Fetch all `lab_results` for `user_id` + `category`, ordered by `date desc`
- Table columns: Test, Result, Unit, Reference Range, Status, Date
- Color-coded Status (reuse `get_status` + `highlight_status` from review.py — copy verbatim, don't import)
- Caption: `N result(s) across all reports`

## Navigation
- Session state approach: `st.session_state["selected_category"]` + `st.switch_page()`
- Refresh on category page loses state → deferred to Day 6 (already in backlog)

## Key Decisions
- Query Supabase directly from Streamlit (no new backend endpoint)
- Group lab_results by category client-side with pandas (avoids Supabase RPC)
- Copy get_status/highlight_status into category.py (cross-page imports are unreliable in Streamlit)

## Watch-outs
- Call `supabase.postgrest.auth(st.session_state.access_token)` inside `show_dashboard()` — the cached client doesn't carry the JWT
- Use `.style.map()` not `.style.applymap()` (deprecated)
- Use `width="stretch"` not `use_container_width=True` (deprecated)
