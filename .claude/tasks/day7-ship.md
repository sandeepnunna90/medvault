# Day 7: Smoke Test + Ship + Beta Launch (v0.1.0)

## Goal
Get the existing app working end-to-end in production and tag v0.1.0. No new features.

## Tasks
- [ ] 1. Push Day 6 commit to origin/main
- [ ] 2. Apply pending Supabase migration (drop_storage_trigger)
- [ ] 3. Verify Render env vars: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, ANTHROPIC_API_KEY
- [ ] 4. Verify Streamlit Cloud secrets: SUPABASE_URL, SUPABASE_ANON_KEY, BACKEND_URL, FRONTEND_URL
- [ ] 5. Confirm Render deploy is live — hit /health
- [ ] 6. Confirm Streamlit Cloud deploy is live — load the app
- [ ] 7. Run 7 smoke test paths against production URLs
- [ ] 8. Fix any blockers found in smoke tests
- [ ] 9. Add `.env.example` (backend keys, no values)
- [ ] 10. Update README: deployed URLs, cold-start caveat, spaCy note
- [ ] 11. Commit pre-launch changes, tag v0.1.0, push tag + create GitHub release

---

## Step 1: Push Day 6 Commit
```bash
git push origin main
```

## Step 2: Apply Pending Supabase Migration
`supabase/migrations/20260325000001_drop_storage_trigger.sql` — drops the storage cascade trigger that blocks delete operations.
```bash
SUPABASE_ACCESS_TOKEN=<token> npx supabase db push --project-ref <project-ref>
```
Or verify manually in Supabase dashboard > Database > Functions that `delete_report_storage_object` no longer exists.

## Step 3: Render Environment Variables
In Render dashboard > medvault-api > Environment:

| Key | Source |
|---|---|
| `SUPABASE_URL` | Supabase dashboard > Settings > API |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase dashboard > Settings > API |
| `ANTHROPIC_API_KEY` | Anthropic console |

`ANTHROPIC_API_KEY` is NOT in render.yaml — must be added manually.

## Step 4: Streamlit Cloud Secrets
In share.streamlit.io > medvault-io > Settings > Secrets:
```toml
SUPABASE_URL = "https://<project>.supabase.co"
SUPABASE_ANON_KEY = "<anon key>"
BACKEND_URL = "https://medvault-rovb.onrender.com"
FRONTEND_URL = "https://medvault-io.streamlit.app"
```
`BACKEND_URL` is production-critical — missing = all uploads and deletes silently fail.

## Step 5-6: Verify Deploys
- Render: `curl https://medvault-rovb.onrender.com/health` → `{"status":"ok"}`
- Streamlit: load https://medvault-io.streamlit.app — auth page should appear

---

## Step 7: Smoke Test Paths

**Path 1 — Sign Up**
- Sign up with new email, confirm email, log in

**Path 2 — Upload**
- Upload a digital PDF lab report
- Expect: "Extraction complete — N test(s) found." with N > 0
- Check OCR text and Cleaned text expandable sections

**Path 3 — Dashboard**
- Metrics: Reports=1, Tests=N, Categories=M
- Category expanders with color-coded tables
- Abnormal values show red/orange

**Path 4 — Trends**
- Click "📈 Trends" on a category
- Select a test — Plotly chart renders with reference range band

**Path 5 — Review + Delete**
- Review page shows uploaded report's tests
- Delete report → disappears from dropdown
- Dashboard shows 0 reports/tests

**Path 6 — Session persistence** (known issue — deferred)
- Refreshing sub-pages may show "Please log in first"
- Workaround for beta users: navigate from Dashboard

**Path 7 — Log Out**
- Logout → auth page shown
- Revisiting app does not auto-restore session

---

## Step 8-10: Pre-Launch Cleanup

### .env.example (new file)
```
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
ANTHROPIC_API_KEY=
```

### README updates needed
- Add deployed URLs
- Add cold-start caveat (Render free tier spins down after 15 min; first request ~30s)
- Check spaCy model download step — remove if pii_stripper.py doesn't actually use spaCy at runtime

### CORS note (non-blocking for beta)
`backend/main.py` has `allow_origins=["*"]` — acceptable for beta, restrict post-launch.

---

## Step 11: Tag v0.1.0
```bash
git tag -a v0.1.0 -m "Beta launch: upload, extract, dashboard, trends, delete"
git push origin v0.1.0
gh release create v0.1.0 --title "v0.1.0 — Beta Launch" \
  --notes "First public beta of MedVault. Upload lab reports (PDF/JPG/PNG), Claude AI extracts structured results, dashboard shows categories and trends over time.

Known limitation: refreshing sub-pages may show login prompt — navigate from Dashboard as workaround."
```

---

## Known Limitations (document, don't block)
1. Sub-page refresh session persistence unreliable (cookie timing — fix deferred post-Day 7)
2. Render free tier cold starts: ~30s for first request after 15 min idle
3. CORS is open (`allow_origins=["*"]`) — restrict post-launch
4. Google OAuth not implemented — email/password only
5. OCR quality lower on scanned (non-digital) PDFs
