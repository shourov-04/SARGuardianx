-- Harden privileges on future public objects created by the Monorepo's
-- postgres-owned application migrations.
--
-- Existing tables/functions are intentionally unchanged. Supabase-managed
-- objects created as supabase_admin are outside this migration: the connected
-- postgres role cannot assume supabase_admin, and we do not modify its ACLs.
--
-- Table and sequence defaults are revoked only in public. Function EXECUTE
-- for PUBLIC is a PostgreSQL global default, so its postgres-owner default is
-- revoked globally; explicit grants on existing functions are unaffected.
-- service_role's existing default grants are deliberately preserved.
--
-- Apply this only after reviewing the Supabase CLI migration-history mapping.

begin;

alter default privileges for role postgres in schema public
  revoke all on tables from anon, authenticated;

alter default privileges for role postgres in schema public
  revoke all on sequences from anon, authenticated;

alter default privileges for role postgres in schema public
  revoke execute on functions from anon, authenticated;

alter default privileges for role postgres
  revoke execute on functions from public;

commit;
