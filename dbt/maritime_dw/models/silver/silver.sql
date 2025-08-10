{{ config(
    materialized='incremental',
    unique_key='unique_row_id'
) }}

with bronze as (

    select
        unique_row_id,
        user_id,
        name,
        imo_number,
        latitude::float,
        longitude::float,
        speed_over_ground,
        navigational_status::int,
        destination,

        -- ETA components
        nullif((eta->>'Month')::int, 0) as eta_month,
        nullif((eta->>'Day')::int, 0) as eta_day,
        nullif((eta->>'Hour')::int, 25) as eta_hour,   -- treat invalid hours as NULL
        nullif((eta->>'Minute')::int, 60) as eta_minute,  -- treat invalid minutes as NULL

        -- ETA parsed timestamp with leap year check for Feb 29
        case 
            when nullif((eta->>'Month')::int, 0) = 2
             and nullif((eta->>'Day')::int, 0) = 29
             and not (
              extract(year from now())::int % 400 = 0 or
              (extract(year from now())::int % 4 = 0 and extract(year from now())::int % 100 != 0)        
             )
            then null
            when nullif((eta->>'Month')::int, 0) is not null
             and nullif((eta->>'Day')::int, 0) is not null
             and nullif((eta->>'Hour')::int, 25) is not null
             and nullif((eta->>'Minute')::int, 60) is not null
            then
                make_timestamp(
                    extract(year from now())::int,
                    (eta->>'Month')::int,
                    (eta->>'Day')::int,
                    (eta->>'Hour')::int,
                    (eta->>'Minute')::int,
                    0
                )
            else null
        end as eta_timestamp,

        type::int,

        _airbyte_extracted_at

    from {{ ref('bronze_clean') }}
    where name is not null and eta is not null and destination is not null
    AND (eta->>'Hour')::int BETWEEN 0 AND 24

),

silver as (
    select
        b.*,
        s.vessel_group AS vessel_description
    from bronze b
    left join {{ ref('ship_types') }} s
      on b.type = s.vessel_type
)

select *
from silver
