{{ config(materialized='table') }}

select
    unique_row_id,
    destination_country,
    vessel_description,
    eta_date,
    distance_to_destination_kilometers,
    speed_over_ground_knots,
    speed_over_ground_knots * 1.852 as speed_over_ground_kmh,
    -- tiempo estimado en horas = distancia(km) / velocidad(kmh)
    case 
      when speed_over_ground_knots > 0 and distance_to_destination_kilometers is not null then
        distance_to_destination_kilometers / (speed_over_ground_knots * 1.852)
      else null
    end as estimated_hours_to_destination,
    -- fecha estimada basada en la velocidad y distancia
    case 
      when speed_over_ground_knots > 0 and distance_to_destination_kilometers is not null then
        current_date + (distance_to_destination_kilometers / (speed_over_ground_knots * 1.852)) * interval '1 hour'
      else null
    end as estimated_arrival_timestamp,
    -- diferencia en días entre ETA reportado y la fecha estimada calculada
    case 
      when eta_date is not null and speed_over_ground_knots > 0 and distance_to_destination_kilometers is not null then
        eta_date - date( current_date + (distance_to_destination_kilometers / (speed_over_ground_knots * 1.852)) * interval '1 hour')
      else null
    end as eta_vs_estimated_days_diff

from {{ ref('gold') }}
where eta_date is not null
  and distance_to_destination_kilometers is not null
  and speed_over_ground_knots > 0
