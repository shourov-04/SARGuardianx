-- Support FK lookups and preflight cleanup joins for processing_jobs.
create index if not exists processing_jobs_preflight_id_idx
  on public.processing_jobs (preflight_id);
