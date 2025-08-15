{{ config(
    materialized='incremental',
    unique_key='unique_row_id'  
) }}

WITH raw_data AS (

    SELECT
        "UserID" AS user_id,
        (_airbyte_meta ->> 'some_key')::text AS airbyte_meta,
        
        "Dte"::boolean AS dte,
        "Eta"::jsonb AS eta,
        ("Eta" ->> 'estimatedTime')::timestamp with time zone AS estimated_time_arrival,

        "Sog"::numeric AS speed_over_ground,
        "MaximumStaticDraught"::numeric AS maximum_static_draught,
        "CommunicationStateIsItdma"::boolean AS communication_state_is_itdma,
        "SpecialManoeuvreIndicator"::bigint AS special_manoeuvre_indicator,
        _airbyte_extracted_at::timestamp with time zone AS _airbyte_extracted_at,
        _airbyte_generation_id::bigint AS _airbyte_generation_id,
        "Cog"::numeric AS course_over_ground,
        "Raim"::boolean AS raim,
        "Type"::bigint AS type,
        "Spare"::bigint AS spare,
        "Valid"::boolean AS valid,
        "Spare1"::bigint AS spare1,
        "Spare2"::bigint AS spare2,
        "FixType"::bigint AS fix_type,
        "Latitude"::numeric AS latitude,
        "ClassBDsc"::boolean AS class_bdsc,
        -- This reflects the full ship length and width, derived from parts
        coalesce(("Dimension" ->> 'A')::numeric, 0) + coalesce(("Dimension" ->> 'B')::numeric, 0) AS dimension_length,
        coalesce(("Dimension" ->> 'C')::numeric, 0) + coalesce(("Dimension" ->> 'D')::numeric, 0) AS dimension_width,


        "ImoNumber"::bigint AS imo_number,
        "Longitude"::numeric AS longitude,
        "MessageID"::bigint AS message_id,
        "Timestamp"::bigint AS time_stamp,
        "AisVersion"::bigint AS ais_version,
        "ClassBBand"::boolean AS class_bband,
        "ClassBUnit"::boolean AS class_bunit,
        "RateOfTurn"::bigint AS rate_of_turn,
        "ClassBMsg22"::boolean AS class_bmsg22,
        "TrueHeading"::bigint AS true_heading,
        "AssignedMode"::boolean AS assigned_mode,
        "ClassBDisplay"::boolean AS class_bdisplay,
        "RepeatIndicator"::bigint AS repeat_indicator,
        "PositionAccuracy"::boolean AS position_accuracy,
        "CommunicationState"::bigint AS communication_state,
        "NavigationalStatus"::bigint AS navigational_status,
        "Name"::varchar AS name,
        _ab_source_file_last_modified::varchar AS _ab_source_file_last_modified,
        _ab_source_file_url::varchar AS _ab_source_file_url,
        _airbyte_raw_id::varchar AS _airbyte_raw_id,
        "CallSign"::varchar AS call_sign,
        "Destination"::varchar AS destination,

        -- unique id: userid + timestamp dbt uses this key for incremental inserts and updates.
        "UserID" || '_' || _airbyte_extracted_at::text AS unique_row_id

    FROM {{ source('raw_data', 'bronze') }}

),

deduped AS (

    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY user_id
            ORDER BY _airbyte_extracted_at DESC
        ) AS row_num
    FROM raw_data

)

SELECT
    *
FROM deduped
WHERE row_num = 1

{% if is_incremental() %}
  AND _airbyte_extracted_at >= (SELECT MAX(_airbyte_extracted_at) FROM {{ this }})
{% endif %}



