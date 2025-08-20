{{ config(materialized='table') }}

with base as (
    select * from {{ ref('gold') }}
)

select
    _airbyte_extracted_at::date as extracted_date,
    vessel_flag_country,
    avg(speed_over_ground_kmh) as avg_speed_kmh,
    max(speed_over_ground_kmh) as max_speed_kmh,
    min(speed_over_ground_kmh) as min_speed_kmh,
    count(distinct unique_row_id) as vessel_count
from base
group by _airbyte_extracted_at::date, vessel_flag_country
order by extracted_date, vessel_flag_country
