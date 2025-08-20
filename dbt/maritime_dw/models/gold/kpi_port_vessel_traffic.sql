{{ config(materialized='table') }}

select
    port_name,
    count(*) as vessel_visits
from {{ ref('gold') }}
where port_name is not null
group by port_name
order by vessel_visits desc
limit 20
