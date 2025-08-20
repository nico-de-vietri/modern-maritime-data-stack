{{ config(materialized='table') }}

select
    case 
        when vessel_flag_country = 'USA' then 'United States'
        else vessel_flag_country
    end as vessel_flag_country,
    count(*) as vessel_count
from {{ ref('gold') }}
group by 
    case 
        when vessel_flag_country = 'USA' then 'United States'
        else vessel_flag_country
    end
order by 
    vessel_flag_country, 
    vessel_count desc
