{{
    config(
        materialized='view',
        tags=['staging']
    )
}}

WITH source AS (
    SELECT * FROM {{ source('postgres', 'products') }}
),

renamed AS (
    SELECT
        -- IDs
        id AS product_id,

        -- Attributes
        name AS product_name,
        category,
        subcategory,
        price,
        cost,
        sku,

        -- Metadata
        created_at,
        updated_at

    FROM source
)

SELECT * FROM renamed
