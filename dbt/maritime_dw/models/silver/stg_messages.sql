{{ config(materialized='incremental', unique_key='unique_row_id') }}

    select
        unique_row_id,
        user_id,
        left(user_id::text, 3)::int as mid,
        _airbyte_extracted_at

    from {{ ref('bronze_messages') }} 
    --where user_id is not null
