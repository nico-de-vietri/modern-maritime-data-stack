{{ config(
    materialized='incremental',
    unique_key='unique_row_id'
) }}

with raw_messages AS (
    select
        "UserID" AS user_id,
        "MessageID"::bigint AS message_id,
        _airbyte_generation_id::bigint AS airbyte_generation_id,
        _airbyte_extracted_at::timestamp with time zone AS _airbyte_extracted_at,
        "Timestamp"::bigint AS timestamp_raw,
        "AisVersion"::bigint AS ais_version,
        --_ab_source_file_last_modified::varchar AS source_file_last_modified,
        _ab_source_file_url::varchar AS source_file_url,
        _airbyte_raw_id::varchar AS airbyte_raw_id,
        "UserID" || '_' || _airbyte_extracted_at::text AS unique_row_id,
        row_number() over (partition by "UserID" order by _airbyte_extracted_at desc) as row_num
    from {{ source('raw_data', 'bronze') }}
)

select *
from raw_messages
where row_num = 1

/*{% if is_incremental() %}
  and _airbyte_extracted_at > (select max(_airbyte_extracted_at) from {{ this }})
{% endif %}*/
