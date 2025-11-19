-- Flyway Migration V3: Rename Column - Phase 1 (EXPAND)
-- Description: Add new column 'full_name' alongside existing 'first_name' and 'last_name'
-- This is part of expand-contract pattern for renaming columns safely
-- IMPORTANT: This does NOT remove old columns - that happens in a later migration
-- Author: DevOps Team
-- Date: 2024-03-01

-- Phase 1: EXPAND - Add new column
ALTER TABLE users
ADD COLUMN full_name VARCHAR(200);

-- Backfill data from existing columns (in batches to avoid long locks)
-- This is safe because it's nullable and we're not removing old columns yet
DO $$
DECLARE
    batch_size INTEGER := 10000;
    total_updated INTEGER := 0;
    rows_updated INTEGER;
BEGIN
    LOOP
        -- Update batch
        WITH batch AS (
            SELECT id
            FROM users
            WHERE full_name IS NULL
                AND (first_name IS NOT NULL OR last_name IS NOT NULL)
            LIMIT batch_size
        )
        UPDATE users u
        SET full_name = TRIM(COALESCE(u.first_name, '') || ' ' || COALESCE(u.last_name, ''))
        FROM batch b
        WHERE u.id = b.id;

        GET DIAGNOSTICS rows_updated = ROW_COUNT;
        total_updated := total_updated + rows_updated;

        -- Exit if no more rows to update
        EXIT WHEN rows_updated = 0;

        -- Log progress
        RAISE NOTICE 'Backfilled % rows (total: %)', rows_updated, total_updated;

        -- Small delay to avoid overloading database
        PERFORM pg_sleep(0.1);
    END LOOP;

    RAISE NOTICE 'Backfill complete: % total rows updated', total_updated;
END $$;

-- Create index on new column
CREATE INDEX idx_users_full_name ON users(full_name);

-- Create trigger to keep full_name in sync with first_name and last_name
-- This ensures dual-write during transition period
CREATE OR REPLACE FUNCTION sync_full_name()
RETURNS TRIGGER AS $$
BEGIN
    -- Update full_name when first_name or last_name changes
    IF NEW.first_name IS DISTINCT FROM OLD.first_name
       OR NEW.last_name IS DISTINCT FROM OLD.last_name THEN
        NEW.full_name := TRIM(COALESCE(NEW.first_name, '') || ' ' || COALESCE(NEW.last_name, ''));
    END IF;

    -- Update first_name and last_name when full_name changes
    -- (for backward compatibility during migration)
    IF NEW.full_name IS DISTINCT FROM OLD.full_name AND NEW.full_name IS NOT NULL THEN
        -- Simple split on first space
        NEW.first_name := SPLIT_PART(NEW.full_name, ' ', 1);
        NEW.last_name := SUBSTRING(NEW.full_name FROM LENGTH(SPLIT_PART(NEW.full_name, ' ', 1)) + 2);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sync_full_name_trigger
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION sync_full_name();

COMMENT ON COLUMN users.full_name IS 'User full name (replaces first_name + last_name)';

-- NOTE: The old columns (first_name, last_name) are still present
-- They will be removed in a future migration (V4__rename_column_contract.sql)
-- after we verify the new column is working correctly in production
