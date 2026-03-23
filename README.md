# MedVault — Personal Health Records Platform

Upload medical test reports. AI extracts your data. See trends over time.

## What it does
- Upload PDF or photo of lab reports
- AI extracts test names, values, units, reference ranges
- Dashboard organizes results by medical category
- Trend graphs show how your values change over time

## ⚠️ Disclaimer
MedVault is a data organization tool. It does not provide
medical advice, diagnoses, or treatment recommendations.

## Setup
1. Clone this repo
2. Copy `.env.example` to `.env` and fill in your keys
3. `pip install -r requirements.txt`
4. `python -m spacy download en_core_web_sm`
5. Start backend: `uvicorn backend.main:app --reload`
6. Start frontend: `streamlit run frontend/app.py`

## Architecture
Streamlit (UI) → FastAPI (API) → Supabase (DB/Auth/Storage) + Claude (extraction)