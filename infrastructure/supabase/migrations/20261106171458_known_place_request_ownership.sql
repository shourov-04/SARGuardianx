-- Private owner mapping for Known Place GitHub request IDs.
-- Stores only correlation/ownership metadata; no AOI, polygon, or science payload.
begin;

create table public.known_place_requests (
  request_id uuid primary key,
  owner_uid text not null check (length(btrim(owner_uid)) > 0),
  request_kind text not null check (request_kind in ('generic', 'paper_reproduction')),
  dispatch_state text not null default 'dispatching'
    check (dispatch_state in ('dispatching', 'dispatched', 'dispatch_failed')),
  created_at timestamptz not null default now()
);

comment on table public.known_place_requests is
  'Private server-side owner mapping for Known Place workflow request IDs; no AOI or science payload is stored.';

alter table public.known_place_requests enable row level security;

-- Default privileges were hardened for public tables. Revoke browser and
-- default grants explicitly, then allow only the API server's service role.
revoke all on table public.known_place_requests from public, anon, authenticated, service_role;
grant select, insert, update on table public.known_place_requests to service_role;

commit;
