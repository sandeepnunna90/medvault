# Day 3: Claude Extraction Engine

**Goal:** Upload a lab report → Claude extracts all test values → structured JSON saved to DB → review table displayed in UI.

## New Files
```
backend/
  extraction.py               — Claude API call + Pydantic validation
frontend/
  pages/review.py             — review table with color-coded status
supabase/migrations/
  20260323000002_create_lab_results_table.sql
```

## Modified Files
- `backend/routers/reports.py` — call extraction after OCR, insert lab_results
- `.claude/tasks/day3-claude-extraction.md` — this file

## Steps
- [x] 1. Create supabase/migrations/002 — lab_results table + RLS
- [x] 2. Run migration via supabase db push
- [x] 3. Build backend/extraction.py (Claude API + Pydantic LabResult model)
- [x] 4. Update backend/routers/reports.py (call extraction, insert lab_results)
- [x] 5. Build frontend/pages/review.py (report selector + styled dataframe)
- [x] 6. Test locally — uploaded CBC PDF, 14 tests extracted at 97% confidence, color-coded table displayed
- [ ] 7. Commit + deploy

## Key Decisions
- Extraction is auto-triggered during upload (not a separate endpoint) — single button UX
- Claude model: claude-sonnet-4-6
- Pydantic validates each extracted test; invalid items are skipped silently
- lab_results table stores one row per test, linked to reports.id
- Review page reads from Supabase directly via anon key + RLS (no backend call needed)
- Status (High/Low/Normal) computed client-side by comparing value to reference range

## Watch-outs
- Render free tier 30s timeout — CBC report with ~10 tests takes ~5-8s including Claude call
- Claude occasionally wraps JSON in markdown fences — strip them in extraction.py
- value stored as TEXT (not numeric) to handle "Borderline", "Positive", etc.
- applymap deprecated in newer pandas — use map() if warnings appear
