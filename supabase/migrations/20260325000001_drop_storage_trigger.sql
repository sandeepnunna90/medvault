-- Drop the storage cascade trigger — Supabase blocks direct DELETE on storage.objects.
-- Storage file deletion is handled explicitly via the Storage API in the backend.

DROP TRIGGER IF EXISTS on_report_delete ON reports;
DROP FUNCTION IF EXISTS delete_report_storage_object();
