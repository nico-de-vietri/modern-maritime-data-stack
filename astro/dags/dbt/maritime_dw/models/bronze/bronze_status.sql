{{ config(
    materialized='incremental',
    unique_key='user_id'
) }}

with raw_status as (
    select
        "UserID" as user_id,
        "CommunicationState"::bigint as communication_state,
        "NavigationalStatus"::bigint as navigational_status,
        "RateOfTurn"::bigint as rate_of_turn,
        "Raim"::boolean as raim,
        "Valid"::boolean as valid,
        "PositionAccuracy"::boolean as position_accuracy,
        "ClassBDsc"::boolean as class_bdsc,
        "ClassBBand"::boolean as class_bband,
        "ClassBUnit"::boolean as class_bunit,
        "ClassBMsg22"::boolean as class_bmsg22,
        "ClassBDisplay"::boolean as class_bdisplay,
        _airbyte_extracted_at::timestamp with time zone as _airbyte_extracted_at,
        "UserID" || '_' || _airbyte_extracted_at::text as unique_row_id
    from {{ source('raw_data', 'bronze') }}
),

deduped as (
    select
        *,
        row_number() over (partition by user_id order by _airbyte_extracted_at desc) as row_num
    from raw_status
)

select *
from deduped
WHERE row_num = 1

/*{% if is_incremental() %}
  AND _airbyte_extracted_at > (select MAX(_airbyte_extracted_at) from {{ this }})
{% endif %}*/
