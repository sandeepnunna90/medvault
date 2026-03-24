-- Migration 002: Create lab_results table
-- Stores structured test results extracted by Claude from each report

CREATE TABLE IF NOT EXISTS lab_results (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id            UUID NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    user_id              UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    test_name            TEXT NOT NULL,
    value                TEXT NOT NULL,
    unit                 TEXT,
    reference_range_low  NUMERIC,
    reference_range_high NUMERIC,
    date                 DATE,
    lab_source           TEXT,
    category             TEXT,
    confidence           INTEGER,
    uploaded_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE lab_results ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can insert own lab results"
ON lab_results FOR INSERT
TO authenticated
WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can read own lab results"
ON lab_results FOR SELECT
TO authenticated
USING (user_id = auth.uid());

CREATE POLICY "Users can update own lab results"
ON lab_results FOR UPDATE
TO authenticated
USING (user_id = auth.uid());

CREATE POLICY "Users can delete own lab results"
ON lab_results FOR DELETE
TO authenticated
USING (user_id = auth.uid());
