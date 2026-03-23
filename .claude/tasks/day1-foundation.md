# Day 1: Foundation + Deploy Skeleton

**Goal:** A deployed Streamlit app with login/signup authenticating against Supabase, plus a FastAPI backend returning health checks.

## File Structure

```
medvault/                    <- repo root
├── .claude/tasks/           <- this file
├── backend/
│   ├── __init__.py
│   └── main.py
├── frontend/
│   ├── __init__.py
│   └── app.py
├── tests/
│   └── __init__.py
├── .streamlit/
│   └── config.toml
├── .env.example
├── .gitignore               <- updated
├── render.yaml
├── requirements.txt
└── requirements-lock.txt
```

## Steps

- [x] 1. Update .gitignore (add medvault/ venv, __pycache__, .DS_Store)
- [x] 2. Create folder structure (backend/, frontend/, tests/, __init__.py files)
- [x] 3. Create .env.example
- [x] 4. Build backend/main.py (FastAPI, CORS, /health, Supabase client)
- [x] 5. Build frontend/app.py (Streamlit login/signup/dashboard)
- [x] 6. Create render.yaml
- [x] 7. Create .streamlit/config.toml (optional theme)
- [x] 8. Manual Supabase setup (project, disable email confirmation for dev)
- [x] 9. Deploy to Render + Streamlit Cloud
- [x] 10. Verify end-to-end

## Deployed URLs
- Backend: https://medvault-rovb.onrender.com
- Frontend: https://medvault-io.streamlit.app

## Key Decisions

- Frontend authenticates directly with Supabase anon key (no backend call for auth) — standard Supabase pattern
- Backend uses service role key — never exposed to frontend
- `requirements-lock.txt` used for Render build command for reproducible deploys
- CORS is `allow_origins=["*"]` for Day 1; restrict to Streamlit Cloud URL once known
- Email confirmation disabled in Supabase dashboard during dev

## Watch Out For

- supabase-py v2 uses `sign_in_with_password({"email": ..., "password": ...})` — dict, not kwargs
- Render requires `--host 0.0.0.0` and `--port $PORT` in start command
- Render free tier has cold starts (~30s) — hit /health before demos
- `medvault/` venv at repo root — confirm .gitignore excludes it before pushing

## Verification Checklist

- [ ] `uvicorn backend.main:app --reload` starts locally
- [ ] GET /health returns `{"status": "ok"}`
- [ ] `streamlit run frontend/app.py` starts locally
- [ ] Sign up creates user in Supabase Auth dashboard
- [ ] Login redirects to dashboard placeholder
- [ ] Logout returns to login
- [ ] Render deploy: /health reachable at public URL
- [ ] Streamlit Cloud deploy: login works at public URL
