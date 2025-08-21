{{ config(
    materialized='incremental',
    unique_key='unique_row_id'
) }}

with raw_destinations as (
    select
        "UserID" as user_id,
        "Destination"::varchar as destination,
        "Eta"::jsonb as eta,
        ("Eta" ->> 'estimatedTime')::timestamp with time zone as estimated_time_arrival,
        _airbyte_extracted_at::timestamp with time zone as _airbyte_extracted_at,
        "UserID" || '_' || _airbyte_extracted_at::text as unique_row_id
    from {{ source('raw_data', 'bronze') }}
),

deduped as (
    select
        *,
        row_number() over (
            partition by user_id
            order by _airbyte_extracted_at desc
        ) as row_num
    from raw_destinations
)

select *
from deduped
where row_num = 1

/*{% if is_incremental() %}
  and _airbyte_extracted_at > (select max(_airbyte_extracted_at) from {{ this }})
{% endif %}*/

