{{ config(
    materialized='incremental',
    unique_key='_airbyte_extracted_at'
) }}


with raw_positions as (
    select
        "UserID" as user_id,
        "Latitude"::numeric as latitude,
        "Longitude"::numeric as longitude,
        "Sog"::numeric as speed_over_ground,
        "Cog"::numeric as course_over_ground,
        "TrueHeading"::bigint as true_heading,
        "Timestamp"::bigint as time_stamp,
        _airbyte_extracted_at::timestamp with time zone as _airbyte_extracted_at,
        "ImoNumber"::bigint as imo_number,
        row_number() OVER (
          PARTITION BY "UserID" 
          ORDER BY _airbyte_extracted_at DESC, "Timestamp" DESC
        ) as row_num
    from {{ source('raw_data', 'bronze') }}
)

select *
from raw_positions
where row_num = 1

/*{% if is_incremental() %}
  and _airbyte_extracted_at > (select MAX(_airbyte_extracted_at) from {{ this }})
{% endif %}*/
