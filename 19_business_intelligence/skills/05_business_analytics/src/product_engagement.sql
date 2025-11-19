-- Business Analytics SQL Query
-- Purpose: Production-ready analytical query

WITH base_data AS (
    SELECT 
        *,
        CURRENT_DATE as analysis_date
    FROM source_table
    WHERE date >= CURRENT_DATE - INTERVAL '90 days'
)
SELECT
    metric_dimension,
    COUNT(DISTINCT entity_id) as total_count,
    SUM(metric_value) as total_value,
    AVG(metric_value) as avg_value
FROM base_data
GROUP BY 1
ORDER BY 2 DESC;
