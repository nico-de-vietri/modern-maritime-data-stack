{{ config(materialized='table') }}

select
    distinct user_id,
    vessel_description,
    speed_over_ground_knots,
    dimension_length_meters,
    dimension_width_meters,
    -- Área aproximada como proxy del tamaño general del barco
    dimension_length_meters * dimension_width_meters as vessel_area_m2
from {{ ref('gold') }}
where speed_over_ground_knots is not null
  and dimension_length_meters is not null
  and dimension_width_meters is not null
  and speed_over_ground_knots > 0
  and dimension_length_meters > 0
  and dimension_width_meters > 0
