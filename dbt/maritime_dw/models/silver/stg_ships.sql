{{ config(materialized='incremental', unique_key='_airbyte_extracted_at') }}
    select
        _airbyte_extracted_at,
        trim(name) as name,
        dimension_length::int,
        dimension_width::int,
        type::int,
        imo_number
        
    from {{ ref('bronze_ships') }}
    where name is not null 