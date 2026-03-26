# MedVault — Personal Health Records Platform

Upload medical test reports. AI extracts your data. See trends over time.

**Live app:** https://medvault-io.streamlit.app
**Backend API:** https://medvault-rovb.onrender.com/health

> **Cold-start note:** The backend runs on Render's free tier and spins down after 15 minutes of inactivity. The first upload after idle may take ~30 seconds while the service wakes up.

## What it does
- Upload PDF or photo of lab reports
- AI extracts test names, values, units, reference ranges
- Dashboard organizes results by medical category
- Trend graphs show how your values change over time
- Delete unwanted reports

## ⚠️ Disclaimer
MedVault is a data organization tool. It does not provide
medical advice, diagnoses, or treatment recommendations.

## Setup
1. Clone this repo
2. Copy `.env.example` to `.env` and fill in your keys
3. `pip install -r requirements.txt`
4. Start backend: `uvicorn backend.main:app --reload`
5. Start frontend: `streamlit run frontend/app.py`

## Architecture
Streamlit (UI) → FastAPI (API) → Supabase (DB/Auth/Storage) + Claude (extraction)

## Known Limitations
- Refreshing sub-pages (Upload, Review, Trends) may show a login prompt — navigate from the Dashboard as a workaround
- OCR quality is lower on scanned (non-digital) PDFs
- Google OAuth not implemented — email/password only