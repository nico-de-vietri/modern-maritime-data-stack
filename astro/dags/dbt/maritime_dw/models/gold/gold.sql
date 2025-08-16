{{ config(materialized='table') }}

with gold as (
    select distinct *
    from (
        select *,
            row_number() over (partition by unique_row_id order by _airbyte_extracted_at desc) as rn
        from {{ ref('silver') }}
        where eta_timestamp is not null
    ) t
    where rn = 1
)


    select 
        unique_row_id,
        user_id,
        name,
        imo_number,
        cast(latitude as float) as latitude,
        cast(longitude as float) as longitude,
        cast(speed_over_ground as float) as speed_over_ground_knots,
        cast(speed_over_ground as float) * 1.852 as speed_over_ground_kmh,
        cast(course_over_ground as float) as course_over_ground_degrees,
        navigation_status,
        dimension_length as dimension_length_meters,
        dimension_width as dimension_width_meters,
        --mid,
        --eta_timestamp,
        cast(eta_timestamp as date) as eta_date, -- date only for grouping
        type,
        _airbyte_extracted_at,
        upper(vessel_description),
        flag_country as vessel_flag_country,
        --destination_clean,
        destination_country as destination_country_code,
        country_name as destination_country,
        matched_port as port_name,
        latitude_destination,
        longitude_destination,

        -- Haversine distance if current and destination coordinates are present
        case 
            when latitude is not null and longitude is not null 
             and latitude_destination is not null and longitude_destination is not null
            then 
                6371 * acos(
                    cos(radians(latitude)) 
                    * cos(radians(latitude_destination))
                    * cos(radians(longitude_destination) - radians(longitude))
                    + sin(radians(latitude)) * sin(radians(latitude_destination))
                )
            else null
        end as distance_to_destination_kilometers

    from gold
  
