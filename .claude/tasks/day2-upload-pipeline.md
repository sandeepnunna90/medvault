# Day 2: Upload Pipeline + OCR

**Goal:** Upload a PDF or photo through Streamlit, see raw OCR text extracted and displayed on screen.

## New Files
```
backend/
  routers/__init__.py        (new)
  routers/reports.py         (new: POST /reports/upload)
  pdf_parser.py              (new)
  ocr_service.py             (new)
  pii_stripper.py            (new)
frontend/
  pages/upload.py            (new: upload UI + consent notice)
```

## Modified Files
- `backend/main.py` — mount reports router
- `frontend/app.py` — store access_token in session state
- `render.yaml` — add tesseract-ocr to build command

## Supabase Setup (manual, before coding)
1. Create storage bucket `reports` (private, 10MB limit, pdf/jpg/png only)
2. Run storage RLS SQL (users can only access their own folder)
3. Create `reports` table with columns: id, user_id, storage_path, file_name, file_type, ocr_text, cleaned_text, status, error_message, uploaded_at
4. Enable RLS on reports table

## Steps
- [x] 1. Supabase setup (bucket + table + RLS) — via supabase db push + manual bucket creation
- [x] 2. Build backend/pii_stripper.py — regex for SSN, phone (US + 10-digit), email, DOB, PID, age, sex, MRN, NPI
- [x] 3. Build backend/ocr_service.py — Tesseract OCR via pytesseract
- [x] 4. Build backend/pdf_parser.py — digital text layer + scanned fallback at 2x zoom, max 3 pages
- [x] 5. Build backend/routers/reports.py (POST /reports/upload) — JWT auth, storage upload, OCR, DB insert
- [x] 6. Update backend/main.py (mount router)
- [x] 7. Update frontend/app.py (store access_token)
- [x] 8. Build frontend/pages/upload.py — upload UI with privacy consent notice
- [x] 9. Update render.yaml (apt-get tesseract-ocr)
- [ ] 10. Deploy + verify end-to-end (pending — deploy to Render after local test)

## Completed Notes
- Tested locally with Drlogy CBC sample PDF — OCR extraction and PII stripping working
- Migrations moved to supabase/migrations/ (Supabase CLI convention) instead of database/migrations/
- supabase/.temp/ added to .gitignore
- BACKEND_URL changed to localhost for local testing (change back to Render URL before deploying)

## Key Decisions
- Auth: Streamlit sends Supabase JWT as Bearer token; FastAPI verifies via supabase.auth.get_user(token)
- Sync processing: extraction happens within the upload request (no async queue for MVP)
- PDF type detection: if page.get_text() returns < 50 chars total → treat as scanned, run OCR on page images at 2x zoom
- OCR cap: first 3 pages only (Render free tier has 30s request timeout)

## Watch-outs
- PyMuPDF imports as `import fitz` not `import pymupdf`
- Use `uploaded_file.getvalue()` not `uploaded_file.read()` (read() empties the buffer)
- Supabase service role key bypasses RLS — intentional for backend, never expose to frontend
- JWT expires after 1 hour — fine for Day 2
- Render cold starts: hit /health before demo to warm up
