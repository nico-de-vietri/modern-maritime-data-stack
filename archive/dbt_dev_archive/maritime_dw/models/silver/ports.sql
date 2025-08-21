{{ config(
    materialized='ephemeral'
) }}

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