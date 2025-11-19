-- Flyway Migration V2: Add User Preferences
-- Description: Add nullable preferences column to support user settings
-- This is a SAFE migration - adds nullable column, backward compatible
-- Author: DevOps Team
-- Date: 2024-02-01

-- Add preferences column (nullable, so safe to add)
ALTER TABLE users
ADD COLUMN preferences JSONB DEFAULT '{}'::JSONB;

-- Add index for preferences queries
CREATE INDEX idx_users_preferences ON users USING gin(preferences);

-- Add comment
COMMENT ON COLUMN users.preferences IS 'User preferences stored as JSON';

-- Example preferences structure:
-- {
--   "theme": "dark",
--   "notifications": {
--     "email": true,
--     "push": false
--   },
--   "privacy": {
--     "profile_visible": true
--   }
-- }
