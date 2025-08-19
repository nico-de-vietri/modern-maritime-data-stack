{{ config(materialized='table') }}

select
    eta_date,
    destination_country,
    count(distinct unique_row_id) as total_arrivals
from {{ ref('gold') }}
group by eta_date, destination_country
order by eta_date desc, total_arrivals desc
