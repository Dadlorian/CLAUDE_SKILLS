-- Flyway Migration V4: Rename Column - Phase 2 (CONTRACT)
-- Description: Remove old first_name and last_name columns after migration to full_name
-- This is part of expand-contract pattern
-- IMPORTANT: Only run this AFTER deploying code that uses full_name instead of first/last name
-- Author: DevOps Team
-- Date: 2024-04-01

-- Verify data consistency before dropping columns
DO $$
DECLARE
    inconsistent_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO inconsistent_count
    FROM users
    WHERE full_name IS NULL
      AND (first_name IS NOT NULL OR last_name IS NOT NULL);

    IF inconsistent_count > 0 THEN
        RAISE EXCEPTION 'Data inconsistency detected: % rows have first/last name but no full_name', inconsistent_count;
    END IF;

    RAISE NOTICE 'Data consistency check passed';
END $$;

-- Phase 2: CONTRACT - Remove sync trigger (no longer needed)
DROP TRIGGER IF EXISTS sync_full_name_trigger ON users;
DROP FUNCTION IF EXISTS sync_full_name();

-- Remove old columns
-- WARNING: This is a breaking change if old code is still deployed
-- Ensure all application instances are using full_name before running this
ALTER TABLE users DROP COLUMN IF EXISTS first_name;
ALTER TABLE users DROP COLUMN IF EXISTS last_name;

-- Make full_name NOT NULL now that it's the only name field
-- First, handle any NULL values (shouldn't be any if backfill worked)
UPDATE users SET full_name = 'Unknown' WHERE full_name IS NULL;

-- Add NOT NULL constraint
ALTER TABLE users ALTER COLUMN full_name SET NOT NULL;

COMMENT ON COLUMN users.full_name IS 'User full name (required)';

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Column rename complete: first_name and last_name removed, full_name is now the primary name field';
END $$;
