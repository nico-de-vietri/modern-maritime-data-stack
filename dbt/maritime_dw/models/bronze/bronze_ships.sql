{{ config(
    materialized='incremental',
    unique_key='user_id'
) }}

with ranked_ships as (
    select
        "UserID"::bigint as user_id,
        "ImoNumber"::bigint as imo_number,
        "Name"::varchar as name,
        "CallSign"::varchar as call_sign,
        "Type"::bigint as type,
        coalesce(("Dimension" ->> 'A')::numeric, 0) + coalesce(("Dimension" ->> 'B')::numeric, 0) as dimension_length,
        coalesce(("Dimension" ->> 'C')::numeric, 0) + coalesce(("Dimension" ->> 'D')::numeric, 0) as dimension_width,
        _airbyte_extracted_at::timestamp with time zone as _airbyte_extracted_at,
        row_number() OVER (PARTITION BY "ImoNumber" ORDER BY _airbyte_extracted_at desc) as row_num
    from {{ source('raw_data', 'bronze') }}
    where "UserID" is not null
)

select *
from ranked_ships
where row_num = 1

/*{% if is_incremental() %}
  AND _airbyte_extracted_at > (select MAX(_airbyte_extracted_at) from {{ this }})
{% endif %}*/
