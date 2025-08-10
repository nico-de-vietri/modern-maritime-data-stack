{{ config(
    materialized='incremental',
    unique_key='unique_row_id'  
) }}

WITH raw_data AS (

    SELECT
        "UserID",
        -- unnesting & casting jsonb _airbyte_meta
        (_airbyte_meta ->> 'some_key')::text AS airbyte_meta_some_key,
        
        "Dte"::boolean,
        "Eta"::jsonb,
        -- unnesting & casting jsonb Eta
        ("Eta" ->> 'estimatedTime')::timestamp with time zone AS estimated_time_arrival,

        "Sog"::numeric AS SpeedOverGround,
        "MaximumStaticDraught"::numeric,
        "CommunicationStateIsItdma"::boolean,
        "SpecialManoeuvreIndicator"::bigint,
        _airbyte_extracted_at::timestamp with time zone,
        _airbyte_generation_id::bigint,
        "Cog"::numeric AS CourseOverGround,
        "Raim"::boolean,
        "Type"::bigint,
        "Spare"::bigint,
        "Valid"::boolean,
        "Spare1"::bigint,
        "Spare2"::bigint,
        "FixType"::bigint,
        "Latitude"::numeric,
        "ClassBDsc"::boolean,
        -- -- unnesting & casting jsonb
        ("Dimension" ->> 'length')::numeric AS dimension_length,
        ("Dimension" ->> 'width')::numeric AS dimension_width,

        "ImoNumber"::bigint,
        "Longitude"::numeric,
        "MessageID"::bigint,
        "Timestamp"::bigint,
        "AisVersion"::bigint,
        "ClassBBand"::boolean,
        "ClassBUnit"::boolean,
        "RateOfTurn"::bigint,
        "ClassBMsg22"::boolean,
        "TrueHeading"::bigint,
        "AssignedMode"::boolean,
        "ClassBDisplay"::boolean,
        "RepeatIndicator"::bigint,
        "PositionAccuracy"::boolean,
        "CommunicationState"::bigint,
        "NavigationalStatus"::bigint,
        "Name"::varchar,
        _ab_source_file_last_modified::varchar,
        _ab_source_file_url::varchar,
        _airbyte_raw_id::varchar,
        "CallSign"::varchar,
        "Destination"::varchar,

        -- unique id  UserID + timestamp for dedup:
        "UserID" || '_' || _airbyte_extracted_at::text AS unique_row_id

    FROM {{ source('raw_data', 'bronze') }}

),

deduped AS (

    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY "UserID"
            ORDER BY _airbyte_extracted_at DESC
        ) AS row_num
    FROM raw_data

)

SELECT
    -- most recent row by UserID
    *
FROM deduped
WHERE row_num = 1

{% if is_incremental() %}
  AND _airbyte_extracted_at > (SELECT MAX(_airbyte_extracted_at) FROM {{ this }})
{% endif %}

