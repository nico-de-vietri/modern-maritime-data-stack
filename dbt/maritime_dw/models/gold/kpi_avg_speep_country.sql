{{ config(materialized='table') }}

SELECT
  vessel_flag_country,
  AVG(speed_over_ground_knots) AS avg_speed_knots,
  COUNT(DISTINCT unique_row_id) AS vessel_count
FROM {{ ref('gold') }}
WHERE vessel_flag_country IS NOT NULL
  AND speed_over_ground_knots IS NOT NULL
GROUP BY 1
ORDER BY avg_speed_knots DESC
LIMIT 10

