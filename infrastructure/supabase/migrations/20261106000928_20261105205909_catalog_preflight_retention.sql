-- Retain expired catalogue preflight snapshots for a 7-day support grace period,
-- then purge only rows that are not referenced by a processing_jobs record.
-- Durable processing job history and all scientific result/artifact manifests are
-- deliberately retained; their retention windows require a separate policy.
begin;

-- Supabase Cron is backed by pg_cron. This migration creates one daily cleanup job.
create extension if not exists pg_cron;

create index if not exists catalog_preflights_expiry_idx
  on public.catalog_preflights (expires_at, id);

-- Keep the existing immutability guard intact for ordinary UPDATE/DELETE.
-- The sole exception is a DELETE performed inside the owner-only SECURITY DEFINER
-- purge function below, in a transaction-local context, as the postgres role.
create or replace function public.enforce_catalog_preflight_immutable()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  if tg_op = 'DELETE'
     and current_setting('sarguardian.retention_purge', true) = 'on'
     and current_user = 'postgres' then
    return old;
  end if;

  raise exception 'catalog preflight snapshots are immutable'
    using errcode = '55000';
end;
$$;

create or replace function public.purge_expired_catalog_preflights()
returns integer
language plpgsql
security definer
set search_path = ''
as $$
declare
  previous_purge_setting text;
  deleted_count integer := 0;
begin
  if current_user <> 'postgres' then
    raise exception 'catalog preflight retention purge must run as postgres'
      using errcode = '42501';
  end if;

  previous_purge_setting := current_setting('sarguardian.retention_purge', true);
  perform pg_catalog.set_config('sarguardian.retention_purge', 'on', true);

  with candidates as (
    select p.id
    from public.catalog_preflights as p
    where p.expires_at < pg_catalog.now() - interval '7 days'
      and not exists (
        select 1
        from public.processing_jobs as j
        where j.preflight_id = p.id
      )
    order by p.expires_at asc, p.id asc
    limit 500
    for update skip locked
  )
  delete from public.catalog_preflights as p
  using candidates as c
  where p.id = c.id;

  get diagnostics deleted_count = row_count;

  perform pg_catalog.set_config(
    'sarguardian.retention_purge',
    coalesce(previous_purge_setting, 'off'),
    true
  );

  return deleted_count;
exception
  when others then
    perform pg_catalog.set_config(
      'sarguardian.retention_purge',
      coalesce(previous_purge_setting, 'off'),
      true
    );
    raise;
end;
$$;

revoke all on function public.enforce_catalog_preflight_immutable()
  from public, anon, authenticated, service_role;
revoke all on function public.purge_expired_catalog_preflights()
  from public, anon, authenticated, service_role;
grant execute on function public.purge_expired_catalog_preflights() to postgres;

comment on function public.purge_expired_catalog_preflights() is
  'Daily bounded cleanup: deletes only catalog_preflights expired for more than 7 days and not referenced by processing_jobs. Job history and scientific artifacts are not deleted.';

-- A named schedule is idempotent in Supabase Cron: rescheduling the same exact
-- name replaces its existing definition. Runs daily at 03:20 UTC.
select cron.schedule(
  'sarguardian-expired-preflight-cleanup',
  '20 3 * * *',
  'select public.purge_expired_catalog_preflights();'
);

commit;
