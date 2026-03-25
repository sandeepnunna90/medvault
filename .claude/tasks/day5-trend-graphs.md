# Day 5: Trend Graphs

**Goal:** Plotly line+scatter charts showing lab test values over time with reference range bands. Users can see how a specific test has changed across multiple reports.

## New Files
```
frontend/
  pages/trends.py    (new: category + test selector, Plotly chart)
```

## Modified Files
- `frontend/app.py` — add "📈 Trends" button to each category expander
- `backend/extraction.py` — improved date extraction prompt + extraction logs
- `backend/pii_stripper.py` — removed generic date stripping (was wiping collection dates)

## Steps
- [x] 1. Create `frontend/pages/trends.py`
- [x] 2. Add "📈 Trends" button to category expanders in `frontend/app.py`
- [x] 3. Test locally
- [x] 4. Commit + push + verify on Streamlit Cloud

## Key Decisions
- `go.Figure` (not plotly.express) — needed for layered traces (band + line + colored scatter)
- Date resolution: use `date` from lab_result if available, else `uploaded_at[:10]`
- Reference range: `.mode().iloc[0]` of non-null values (most common across uploads)
- `st.session_state.pop("selected_category", None)` — pop not get, clears stale nav state
- Reference band color: steelblue (changed from green — user preference)

## Watch-outs
- `key=f"trends_{category}"` required — unique widget keys in loops
- Don't import helpers from other pages — copy inline
- Skip line trace if only 1 data point
- Skip band + hlines if no reference range data

## Bugs Fixed During Day 5
- **Dates showing as upload date**: PII stripper was replacing all dates (`MM/DD/YYYY`) with `[DATE]` before Claude saw the text. Fixed by removing the generic date pattern — DOB is still stripped separately.
- **Extraction prompt not finding dates**: Updated Claude system prompt to explicitly look for report-level collection/service/specimen dates and apply to all tests.
- **Failed reports saved on extraction error**: Backend now deletes the report row and storage file on failure instead of marking status=error.
- **Trend band color**: Changed from green to steelblue per user preference.
- **Band corner dots**: Fixed by adding `mode="lines"` to the fill polygon trace.
- **X-axis zooming to milliseconds**: Fixed with `tickformat="%b %d, %Y"` and ±30 day band padding.
