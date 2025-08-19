{{ config(materialized='incremental', unique_key='_airbyte_extracted_at') }}
    select
        _airbyte_extracted_at,
        user_id,
        imo_number,
        latitude::float,
        longitude::float,
        speed_over_ground,
        course_over_ground
    from  {{ ref('bronze_positions') }} 