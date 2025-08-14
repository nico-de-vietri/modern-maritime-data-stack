{{ config(
    materialized='incremental',
    unique_key='unique_row_id'
) }}

with bronze as (

    select
        unique_row_id,
        user_id,
        trim(name) as name,
        imo_number,
        latitude::float,
        longitude::float,
        speed_over_ground,
        navigational_status::int,
        destination,
        dimension_length::int,
        dimension_width::int,
        left(user_id::text, 3)::int as mid,
        

        -- ETA components
        eta,
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

enriched as (
    select
        b.*,
        s.vessel_group as vessel_description,
        c.country as flag_country,
        -- Normalize and clean the destination field
        trim(upper(b.destination)) as destination_clean,

        -- Extract parts for fuzzy match
        split_part(trim(upper(b.destination)), ' ', 1) as dest_country_guess,
        split_part(trim(upper(b.destination)), ' ', 2) as dest_loc_guess

    from bronze b
    left join {{ ref('ship_types') }} s
      on b.type = s.vessel_type
    left join {{ ref('mid_country') }} c
        on b.mid = c.mid
),

ports as (
    select 
        upper(trim(name)) as port_name,
        upper(trim(location)) as location_code,
        upper(trim(country_code)) as country_code,
        coordinates,
        -- Coordinate parts
        split_part(trim(coordinates), ' ', 1) as latitude_raw,
        split_part(trim(coordinates), ' ', 2) as longitude_raw,

        -- Safe decimal conversion for latitude
        case 
            when coordinates is not null 
             and split_part(coordinates, ' ', 1) ~ '^[0-9]{4}[NS]$'
            then (
                (substring(split_part(coordinates, ' ', 1) from 1 for 2)::int + 
                 substring(split_part(coordinates, ' ', 1) from 3 for 2)::int / 60.0) *
                case when right(split_part(coordinates, ' ', 1), 1) = 'S' then -1 else 1 end
            )
            else null
        end as latitude_destination,

        -- Safe decimal conversion for longitude
        case 
            when coordinates is not null 
             and split_part(coordinates, ' ', 2) ~ '^[0-9]{5}[EW]$'
            then (
                (substring(split_part(coordinates, ' ', 2) from 1 for 3)::int + 
                 substring(split_part(coordinates, ' ', 2) from 4 for 2)::int / 60.0) *
                case when right(split_part(coordinates, ' ', 2), 1) = 'W' then -1 else 1 end
            )
            else null
        end as longitude_destination
        
    from {{ ref('port_codes') }}
),

-- Match on name first, fallback on location and country
silver as (
    select
        e.*,
        nv1.description as navigation_status,
        coalesce(
            p1.country_code, 
            p2.country_code
        ) as destination_country,
        cc1.country_name,
        coalesce(
            p1.port_name,
            p2.port_name
        ) as matched_port,
        coalesce(p1.latitude_destination, p2.latitude_destination) as latitude_destination,
        coalesce(p1.longitude_destination, p2.longitude_destination) as longitude_destination

    from enriched e

    -- Primary match on cleaned destination name
    left join ports p1
        on e.destination_clean = p1.port_name

    -- Fallback: match on country & location code
    left join ports p2
        on e.dest_country_guess = p2.country_code
        and e.dest_loc_guess = p2.location_code
    left join {{ ref('country_code') }} cc1
        on p1.country_code=cc1.country_code
    left join {{ ref('navigation_status') }} nv1
        on e.navigational_status=nv1.navigation_status
)

select * 
from silver
{% if is_incremental() %}
where _airbyte_extracted_at > (select coalesce(max(_airbyte_extracted_at), '1900-01-01'::timestamp) FROM {{ this }})
{% endif %}
