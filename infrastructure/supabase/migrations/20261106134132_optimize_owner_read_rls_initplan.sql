drop policy if exists catalog_preflights_owner_read on public.catalog_preflights;
create policy catalog_preflights_owner_read
  on public.catalog_preflights
  for select
  to authenticated
  using (((select auth.jwt()) ->> 'sub') = owner_uid);

drop policy if exists processing_jobs_owner_read on public.processing_jobs;
create policy processing_jobs_owner_read
  on public.processing_jobs
  for select
  to authenticated
  using (((select auth.jwt()) ->> 'sub') = owner_uid);

drop policy if exists displacement_jobs_owner_read on public.displacement_jobs;
create policy displacement_jobs_owner_read
  on public.displacement_jobs
  for select
  to authenticated
  using (((select auth.jwt()) ->> 'sub') = owner_uid);

drop policy if exists river_shift_jobs_owner_read on public.river_shift_jobs;
create policy river_shift_jobs_owner_read
  on public.river_shift_jobs
  for select
  to authenticated
  using (((select auth.jwt()) ->> 'sub') = owner_uid);
