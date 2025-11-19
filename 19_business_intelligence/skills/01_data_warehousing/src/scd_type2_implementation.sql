-- Slowly Changing Dimension Type 2 Implementation
-- Platform-agnostic implementation patterns
-- Description: Complete SCD Type 2 logic for tracking historical changes

-- ============================================
-- PATTERN 1: MERGE-BASED SCD TYPE 2 (Snowflake)
-- ============================================

-- Example: Update Customer Dimension with SCD Type 2 logic
MERGE INTO DIM.DIM_CUSTOMER AS target
USING (
    -- Identify new and changed records from staging
    SELECT
        src.CUSTOMER_ID,
        src.CUSTOMER_NAME,
        src.EMAIL,
        src.PHONE,
        src.CUSTOMER_SEGMENT,
        src.CUSTOMER_TIER,
        src.COUNTRY,
        src.STATE,
        src.CITY,
        src.POSTAL_CODE,
        src.SOURCE_SYSTEM,
        CURRENT_DATE() AS EFFECTIVE_DATE,
        NULL AS EXPIRATION_DATE,
        TRUE AS IS_CURRENT,
        -- Generate hash for change detection
        MD5(
            CONCAT_WS('|',
                COALESCE(src.CUSTOMER_NAME, ''),
                COALESCE(src.EMAIL, ''),
                COALESCE(src.PHONE, ''),
                COALESCE(src.CUSTOMER_SEGMENT, ''),
                COALESCE(src.CUSTOMER_TIER, ''),
                COALESCE(src.COUNTRY, ''),
                COALESCE(src.STATE, ''),
                COALESCE(src.CITY, ''),
                COALESCE(src.POSTAL_CODE, '')
            )
        ) AS ROW_HASH
    FROM STAGING.STG_CUSTOMER src
) AS source
ON target.CUSTOMER_ID = source.CUSTOMER_ID
   AND target.IS_CURRENT = TRUE
WHEN MATCHED AND (
    -- Check if any tracked attributes have changed
    MD5(
        CONCAT_WS('|',
            COALESCE(target.CUSTOMER_NAME, ''),
            COALESCE(target.EMAIL, ''),
            COALESCE(target.PHONE, ''),
            COALESCE(target.CUSTOMER_SEGMENT, ''),
            COALESCE(target.CUSTOMER_TIER, ''),
            COALESCE(target.COUNTRY, ''),
            COALESCE(target.STATE, ''),
            COALESCE(target.CITY, ''),
            COALESCE(target.POSTAL_CODE, '')
        )
    ) != source.ROW_HASH
) THEN UPDATE SET
    IS_CURRENT = FALSE,
    EXPIRATION_DATE = CURRENT_DATE() - 1,
    UPDATED_AT = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN INSERT (
    CUSTOMER_ID,
    CUSTOMER_NAME,
    EMAIL,
    PHONE,
    CUSTOMER_SEGMENT,
    CUSTOMER_TIER,
    COUNTRY,
    STATE,
    CITY,
    POSTAL_CODE,
    EFFECTIVE_DATE,
    EXPIRATION_DATE,
    IS_CURRENT,
    SOURCE_SYSTEM,
    CREATED_AT,
    UPDATED_AT
) VALUES (
    source.CUSTOMER_ID,
    source.CUSTOMER_NAME,
    source.EMAIL,
    source.PHONE,
    source.CUSTOMER_SEGMENT,
    source.CUSTOMER_TIER,
    source.COUNTRY,
    source.STATE,
    source.CITY,
    source.POSTAL_CODE,
    source.EFFECTIVE_DATE,
    source.EXPIRATION_DATE,
    source.IS_CURRENT,
    source.SOURCE_SYSTEM,
    CURRENT_TIMESTAMP(),
    CURRENT_TIMESTAMP()
);

-- Insert new versions for changed records
INSERT INTO DIM.DIM_CUSTOMER (
    CUSTOMER_ID,
    CUSTOMER_NAME,
    EMAIL,
    PHONE,
    CUSTOMER_SEGMENT,
    CUSTOMER_TIER,
    COUNTRY,
    STATE,
    CITY,
    POSTAL_CODE,
    EFFECTIVE_DATE,
    EXPIRATION_DATE,
    IS_CURRENT,
    SOURCE_SYSTEM,
    CREATED_AT,
    UPDATED_AT
)
SELECT
    src.CUSTOMER_ID,
    src.CUSTOMER_NAME,
    src.EMAIL,
    src.PHONE,
    src.CUSTOMER_SEGMENT,
    src.CUSTOMER_TIER,
    src.COUNTRY,
    src.STATE,
    src.CITY,
    src.POSTAL_CODE,
    CURRENT_DATE() AS EFFECTIVE_DATE,
    NULL AS EXPIRATION_DATE,
    TRUE AS IS_CURRENT,
    src.SOURCE_SYSTEM,
    CURRENT_TIMESTAMP(),
    CURRENT_TIMESTAMP()
FROM STAGING.STG_CUSTOMER src
INNER JOIN (
    -- Find records that were just expired
    SELECT CUSTOMER_ID
    FROM DIM.DIM_CUSTOMER
    WHERE IS_CURRENT = FALSE
      AND EXPIRATION_DATE = CURRENT_DATE() - 1
) changed ON src.CUSTOMER_ID = changed.CUSTOMER_ID;

-- ============================================
-- PATTERN 2: STORED PROCEDURE FOR SCD TYPE 2
-- ============================================

CREATE OR REPLACE PROCEDURE SP_LOAD_SCD_TYPE2_DIMENSION(
    SOURCE_TABLE VARCHAR,
    TARGET_TABLE VARCHAR,
    BUSINESS_KEY VARCHAR,
    TRACKED_COLUMNS ARRAY
)
RETURNS STRING
LANGUAGE JAVASCRIPT
AS
$$
    // This procedure implements generic SCD Type 2 logic
    var result = "";

    try {
        // Step 1: Expire changed records
        var expireSQL = `
            UPDATE IDENTIFIER(?) tgt
            SET IS_CURRENT = FALSE,
                EXPIRATION_DATE = CURRENT_DATE() - 1,
                UPDATED_AT = CURRENT_TIMESTAMP()
            FROM IDENTIFIER(?) src
            WHERE tgt.${BUSINESS_KEY} = src.${BUSINESS_KEY}
              AND tgt.IS_CURRENT = TRUE
              AND (
                  -- Add dynamic column comparison here
                  ${TRACKED_COLUMNS.map(col => `tgt.${col} != src.${col}`).join(' OR ')}
              )
        `;

        snowflake.execute({sqlText: expireSQL, binds: [TARGET_TABLE, SOURCE_TABLE]});

        // Step 2: Insert new and changed records
        var insertSQL = `
            INSERT INTO IDENTIFIER(?)
            SELECT
                src.*,
                CURRENT_DATE() AS EFFECTIVE_DATE,
                NULL AS EXPIRATION_DATE,
                TRUE AS IS_CURRENT,
                CURRENT_TIMESTAMP() AS CREATED_AT,
                CURRENT_TIMESTAMP() AS UPDATED_AT
            FROM IDENTIFIER(?) src
            LEFT JOIN (
                SELECT ${BUSINESS_KEY}
                FROM IDENTIFIER(?)
                WHERE IS_CURRENT = TRUE
            ) tgt ON src.${BUSINESS_KEY} = tgt.${BUSINESS_KEY}
            WHERE tgt.${BUSINESS_KEY} IS NULL
               OR EXISTS (
                   SELECT 1
                   FROM IDENTIFIER(?) t
                   WHERE t.${BUSINESS_KEY} = src.${BUSINESS_KEY}
                     AND t.EXPIRATION_DATE = CURRENT_DATE() - 1
               )
        `;

        snowflake.execute({sqlText: insertSQL, binds: [TARGET_TABLE, SOURCE_TABLE, TARGET_TABLE, TARGET_TABLE]});

        result = "SCD Type 2 load completed successfully";
    } catch (err) {
        result = "ERROR: " + err.message;
    }

    return result;
$$;

-- ============================================
-- PATTERN 3: BIGQUERY SCD TYPE 2 MERGE
-- ============================================

-- Step 1: Expire old records
MERGE INTO `project.dwh.dim_customer` AS target
USING (
    SELECT
        s.customer_id,
        s.customer_name,
        s.email,
        s.phone,
        s.customer_segment,
        s.customer_tier,
        s.country,
        s.state,
        s.city,
        s.postal_code,
        -- Generate hash for comparison
        TO_BASE64(MD5(CONCAT(
            IFNULL(s.customer_name, ''), '|',
            IFNULL(s.email, ''), '|',
            IFNULL(s.phone, ''), '|',
            IFNULL(s.customer_segment, ''), '|',
            IFNULL(s.customer_tier, ''), '|',
            IFNULL(s.country, ''), '|',
            IFNULL(s.state, ''), '|',
            IFNULL(s.city, ''), '|',
            IFNULL(s.postal_code, '')
        ))) AS source_hash
    FROM `project.staging.stg_customer` s
) AS source
ON target.customer_id = source.customer_id
   AND target.is_current = TRUE
WHEN MATCHED AND (
    TO_BASE64(MD5(CONCAT(
        IFNULL(target.customer_name, ''), '|',
        IFNULL(target.email, ''), '|',
        IFNULL(target.phone, ''), '|',
        IFNULL(target.customer_segment, ''), '|',
        IFNULL(target.customer_tier, ''), '|',
        IFNULL(target.country, ''), '|',
        IFNULL(target.state, ''), '|',
        IFNULL(target.city, ''), '|',
        IFNULL(target.postal_code, '')
    ))) != source.source_hash
) THEN UPDATE SET
    is_current = FALSE,
    expiration_date = CURRENT_DATE() - 1,
    updated_at = CURRENT_TIMESTAMP();

-- Step 2: Insert new and changed records
INSERT INTO `project.dwh.dim_customer` (
    customer_id,
    customer_name,
    email,
    phone,
    customer_segment,
    customer_tier,
    country,
    state,
    city,
    postal_code,
    effective_date,
    expiration_date,
    is_current,
    row_hash,
    created_at,
    updated_at
)
SELECT
    s.customer_id,
    s.customer_name,
    s.email,
    s.phone,
    s.customer_segment,
    s.customer_tier,
    s.country,
    s.state,
    s.city,
    s.postal_code,
    CURRENT_DATE() AS effective_date,
    NULL AS expiration_date,
    TRUE AS is_current,
    TO_BASE64(MD5(CONCAT(
        IFNULL(s.customer_name, ''), '|',
        IFNULL(s.email, ''), '|',
        IFNULL(s.phone, ''), '|',
        IFNULL(s.customer_segment, ''), '|',
        IFNULL(s.customer_tier, ''), '|',
        IFNULL(s.country, ''), '|',
        IFNULL(s.state, ''), '|',
        IFNULL(s.city, ''), '|',
        IFNULL(s.postal_code, '')
    ))) AS row_hash,
    CURRENT_TIMESTAMP() AS created_at,
    CURRENT_TIMESTAMP() AS updated_at
FROM `project.staging.stg_customer` s
WHERE NOT EXISTS (
    -- Exclude records that haven't changed
    SELECT 1
    FROM `project.dwh.dim_customer` t
    WHERE t.customer_id = s.customer_id
      AND t.is_current = TRUE
      AND TO_BASE64(MD5(CONCAT(
          IFNULL(t.customer_name, ''), '|',
          IFNULL(t.email, ''), '|',
          IFNULL(t.phone, ''), '|',
          IFNULL(t.customer_segment, ''), '|',
          IFNULL(t.customer_tier, ''), '|',
          IFNULL(t.country, ''), '|',
          IFNULL(t.state, ''), '|',
          IFNULL(t.city, ''), '|',
          IFNULL(t.postal_code, '')
      ))) = TO_BASE64(MD5(CONCAT(
          IFNULL(s.customer_name, ''), '|',
          IFNULL(s.email, ''), '|',
          IFNULL(s.phone, ''), '|',
          IFNULL(s.customer_segment, ''), '|',
          IFNULL(s.customer_tier, ''), '|',
          IFNULL(s.country, ''), '|',
          IFNULL(s.state, ''), '|',
          IFNULL(s.city, ''), '|',
          IFNULL(s.postal_code, '')
      )))
);

-- ============================================
-- PATTERN 4: POINT-IN-TIME QUERY EXAMPLES
-- ============================================

-- Query customer attributes as of a specific date
SELECT
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    c.customer_tier,
    c.city,
    c.state
FROM DIM.DIM_CUSTOMER c
WHERE c.customer_id = 'CUST-12345'
  AND '2024-01-15' BETWEEN c.effective_date AND COALESCE(c.expiration_date, '9999-12-31');

-- Get all historical versions of a customer
SELECT
    customer_key,
    customer_id,
    customer_name,
    customer_segment,
    effective_date,
    expiration_date,
    is_current
FROM DIM.DIM_CUSTOMER
WHERE customer_id = 'CUST-12345'
ORDER BY effective_date DESC;

-- Find customers who changed segments in the last 30 days
SELECT
    curr.customer_id,
    curr.customer_name,
    prev.customer_segment AS previous_segment,
    curr.customer_segment AS current_segment,
    curr.effective_date AS change_date
FROM DIM.DIM_CUSTOMER curr
INNER JOIN DIM.DIM_CUSTOMER prev
    ON curr.customer_id = prev.customer_id
    AND prev.expiration_date = curr.effective_date - 1
WHERE curr.is_current = TRUE
  AND curr.effective_date >= CURRENT_DATE() - 30
  AND curr.customer_segment != prev.customer_segment;

-- ============================================
-- PATTERN 5: DATA QUALITY CHECKS
-- ============================================

-- Check for overlapping effective dates (should return 0 rows)
SELECT
    customer_id,
    COUNT(*) AS overlapping_records
FROM (
    SELECT
        c1.customer_id,
        c1.effective_date,
        c1.expiration_date,
        c2.effective_date AS other_effective,
        c2.expiration_date AS other_expiration
    FROM DIM.DIM_CUSTOMER c1
    JOIN DIM.DIM_CUSTOMER c2
        ON c1.customer_id = c2.customer_id
        AND c1.customer_key != c2.customer_key
    WHERE c1.effective_date <= COALESCE(c2.expiration_date, '9999-12-31')
      AND COALESCE(c1.expiration_date, '9999-12-31') >= c2.effective_date
)
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- Check for gaps in history (should return 0 rows)
SELECT
    curr.customer_id,
    prev.expiration_date AS gap_start,
    curr.effective_date AS gap_end,
    DATEDIFF(day, prev.expiration_date, curr.effective_date) AS gap_days
FROM DIM.DIM_CUSTOMER curr
INNER JOIN DIM.DIM_CUSTOMER prev
    ON curr.customer_id = prev.customer_id
    AND prev.expiration_date IS NOT NULL
WHERE curr.effective_date != prev.expiration_date + 1
ORDER BY curr.customer_id, gap_start;

-- Check for multiple current records (should return 0 rows)
SELECT
    customer_id,
    COUNT(*) AS current_record_count
FROM DIM.DIM_CUSTOMER
WHERE is_current = TRUE
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- ============================================
-- PATTERN 6: PERFORMANCE OPTIMIZATION
-- ============================================

-- Create indexes for SCD Type 2 queries (platform-specific)

-- Snowflake: Clustering keys are defined in table DDL
-- ALTER TABLE DIM.DIM_CUSTOMER CLUSTER BY (CUSTOMER_ID, IS_CURRENT);

-- BigQuery: Clustering is defined in table DDL
-- Already specified in CREATE TABLE statements above

-- Redshift: Create indexes
-- CREATE INDEX idx_customer_id_current ON dim_customer (customer_id, is_current);
-- CREATE INDEX idx_customer_effective_date ON dim_customer (effective_date);

-- ============================================
-- PATTERN 7: INCREMENTAL SCD TYPE 2 LOAD
-- ============================================

-- Only process changed records from CDC/incremental source
CREATE OR REPLACE TEMPORARY TABLE TMP_CHANGED_CUSTOMERS AS
SELECT DISTINCT
    src.customer_id
FROM STAGING.STG_CUSTOMER_INCREMENTAL src
LEFT JOIN DIM.DIM_CUSTOMER tgt
    ON src.customer_id = tgt.customer_id
    AND tgt.is_current = TRUE
WHERE tgt.customer_id IS NULL  -- New customer
   OR (  -- Changed customer (any tracked attribute)
       tgt.customer_name != src.customer_name
       OR tgt.email != src.email
       OR tgt.customer_segment != src.customer_segment
       OR tgt.customer_tier != src.customer_tier
   );

-- Only update dimension for changed customers
MERGE INTO DIM.DIM_CUSTOMER AS target
USING (
    SELECT src.*
    FROM STAGING.STG_CUSTOMER_INCREMENTAL src
    INNER JOIN TMP_CHANGED_CUSTOMERS changed
        ON src.customer_id = changed.customer_id
) AS source
ON target.customer_id = source.customer_id
   AND target.is_current = TRUE
-- Continue with standard SCD Type 2 MERGE logic...
WHEN MATCHED THEN UPDATE SET
    is_current = FALSE,
    expiration_date = CURRENT_DATE() - 1,
    updated_at = CURRENT_TIMESTAMP();
