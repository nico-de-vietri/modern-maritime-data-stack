{{ config(materialized='table') }}

select
    port_name,
    count(distinct user_id) as vessel_visits
from {{ ref('gold') }}
group by port_name
order by vessel_visits desc
limit 20
