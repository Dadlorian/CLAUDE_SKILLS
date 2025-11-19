{{
    config(
        materialized='view',
        tags=['staging', 'daily']
    )
}}

WITH source AS (
    SELECT * FROM {{ source('postgres', 'orders') }}
),

renamed AS (
    SELECT
        -- IDs
        id AS order_id,
        customer_id,
        product_id,

        -- Order details
        order_number,
        order_date,
        status,

        -- Amounts
        quantity,
        unit_price,
        discount_amount,
        tax_amount,
        total_amount,

        -- Metadata
        created_at,
        updated_at,
        _loaded_at

    FROM source
)

SELECT * FROM renamed
