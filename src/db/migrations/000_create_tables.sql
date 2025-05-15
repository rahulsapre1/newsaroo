-- Create newsroom_users table if it doesn't exist
CREATE TABLE IF NOT EXISTS newsroom_users (
    id BIGSERIAL PRIMARY KEY,
    mobile_number VARCHAR(15) UNIQUE NOT NULL,
    topics_of_interest TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_newsroom_users_updated_at
    BEFORE UPDATE ON newsroom_users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 