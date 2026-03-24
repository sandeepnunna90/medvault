-- Migration 001: Create reports table + storage bucket RLS
-- Run this against your Supabase project via the SQL editor or Supabase MCP

-- ============================================================
-- 1. Storage bucket (create manually in Supabase dashboard:
--    Storage > New bucket > name: "reports", private, 10MB max)
--    Then apply RLS policies below.
-- ============================================================

-- Storage RLS: users can only read/write inside their own folder (user_id/)
CREATE POLICY "Users can upload to own folder"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'reports' AND (storage.foldername(name))[1] = auth.uid()::text);

CREATE POLICY "Users can read own files"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'reports' AND (storage.foldername(name))[1] = auth.uid()::text);

CREATE POLICY "Users can delete own files"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'reports' AND (storage.foldername(name))[1] = auth.uid()::text);

-- ============================================================
-- 2. Reports table
-- ============================================================

CREATE TABLE IF NOT EXISTS reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    storage_path    TEXT NOT NULL,          -- e.g. "{user_id}/{filename}"
    file_name       TEXT NOT NULL,
    file_type       TEXT NOT NULL,          -- 'pdf', 'jpg', 'png'
    ocr_text        TEXT,                   -- raw OCR output
    cleaned_text    TEXT,                   -- PII-stripped text
    status          TEXT NOT NULL DEFAULT 'pending',  -- pending | processing | done | error
    error_message   TEXT,
    uploaded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 3. RLS on reports table
-- ============================================================

ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can insert own reports"
ON reports FOR INSERT
TO authenticated
WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can read own reports"
ON reports FOR SELECT
TO authenticated
USING (user_id = auth.uid());

CREATE POLICY "Users can update own reports"
ON reports FOR UPDATE
TO authenticated
USING (user_id = auth.uid());

CREATE POLICY "Users can delete own reports"
ON reports FOR DELETE
TO authenticated
USING (user_id = auth.uid());
