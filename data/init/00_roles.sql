
-- 00_roles.sql
-- Create Supabase-compatible roles for PostgREST

-- 1. Web Anon (Public)
CREATE ROLE anon nologin;
GRANT usage ON SCHEMA public TO anon;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO anon;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon;

-- 2. Authenticator (The Gateway)
CREATE ROLE authenticator noinherit login password 'postgres'; -- We use postgres pwd for simplicity in local
GRANT anon TO authenticator;

-- 3. Service Role (Admin Admin)
CREATE ROLE service_role nologin;
GRANT ALL ON SCHEMA public TO service_role;
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT service_role TO authenticator;
