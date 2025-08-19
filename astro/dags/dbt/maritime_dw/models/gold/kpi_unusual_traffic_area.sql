with base as (
    select
        cast(_airbyte_extracted_at as date) as date,
        round(latitude::numeric, 1) as lat_bin,
        round(longitude::numeric, 1) as lon_bin,
        count(distinct user_id) as vessel_count,
        avg(speed_over_ground_kmh) as avg_speed
    from {{ ref('gold') }}
    where latitude is not null and longitude is not null
    group by 1, 2, 3
)

select *
from base
where vessel_count > 10 and avg_speed < 5  
order by vessel_count desc, avg_speed
