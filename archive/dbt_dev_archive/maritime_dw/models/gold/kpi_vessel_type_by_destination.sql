{{ config(materialized='table') }}

select
    destination_country,
    vessel_description,
    count(distinct user_id) as vessel_count
from {{ ref('gold') }}
where destination_country is not null
  and vessel_description is not null
group by 1, 2
order by destination_country, vessel_count desc
