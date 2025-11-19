{{
    config(
        materialized='view',
        tags=['staging', 'daily']
    )
}}

WITH source AS (
    SELECT * FROM {{ source('postgres', 'customers') }}
),

renamed AS (
    SELECT
        -- IDs
        id AS customer_id,

        -- Attributes
        first_name,
        last_name,
        email,
        phone,
        address,
        city,
        state,
        zip_code,
        country,

        -- Metadata
        created_at,
        updated_at,
        _loaded_at

    FROM source
)

SELECT * FROM renamed
