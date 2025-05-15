-- First, disable RLS
ALTER TABLE newsroom_users DISABLE ROW LEVEL SECURITY;

-- Drop existing policies
DROP POLICY IF EXISTS "Enable all for service role" ON newsroom_users;

-- Grant full access to service role
GRANT ALL ON newsroom_users TO service_role;
GRANT USAGE, SELECT ON SEQUENCE newsroom_users_id_seq TO service_role;

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_newsroom_users_mobile ON newsroom_users(mobile_number);

-- Enable RLS but allow service role to bypass it
ALTER TABLE newsroom_users FORCE ROW LEVEL SECURITY;
ALTER TABLE newsroom_users ENABLE ROW LEVEL SECURITY;

-- Allow service role to bypass RLS
ALTER TABLE newsroom_users FORCE ROW LEVEL SECURITY;
ALTER TABLE newsroom_users ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all operations
CREATE POLICY "Allow all operations" ON newsroom_users FOR ALL USING (true);

-- Verify that the service role can bypass RLS
ALTER ROLE service_role BYPASSRLS; 