{{ config(materialized='incremental', unique_key='user_id') }}
    select
        user_id,
        _airbyte_extracted_at,
        trim(name) as name,
        dimension_length::int,
        dimension_width::int,
        type::int,
        imo_number
        
    from {{ ref('bronze_ships') }}
    where name is not null 