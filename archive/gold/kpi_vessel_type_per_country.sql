{{ config(materialized='table') }}

select
    vessel_flag_country,
    vessel_description,
    count(distinct unique_row_id) as vessel_count
from {{ ref('gold') }}
group by vessel_flag_country, vessel_description
order by vessel_flag_country, vessel_count desc
