-- Automatically delete the storage object when a report row is deleted.
-- Supabase stores files in storage.objects, so we can do this directly
-- without any HTTP calls or Edge Functions.

create or replace function delete_report_storage_object()
returns trigger as $$
begin
  delete from storage.objects
  where bucket_id = 'reports' and name = OLD.storage_path;
  return OLD;
end;
$$ language plpgsql security definer;

create trigger on_report_delete
  before delete on reports
  for each row execute function delete_report_storage_object();
