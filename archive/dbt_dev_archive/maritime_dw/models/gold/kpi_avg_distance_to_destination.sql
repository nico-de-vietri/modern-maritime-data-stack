{{ config(materialized='table') }}

select
    eta_date,
    destination_country,
    avg(distance_to_destination_kilometers) as avg_distance_km,
    max(distance_to_destination_kilometers) as max_distance_km,
    count(distinct unique_row_id) as vessel_count
from {{ ref('gold') }}
group by eta_date, destination_country
order by eta_date desc, avg_distance_km desc