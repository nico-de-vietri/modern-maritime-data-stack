{{ config(materialized='table') }}

SELECT
  vessel_description AS vessel_type,
  COUNT(DISTINCT user_id) AS vessel_count
FROM {{ ref('gold') }}
WHERE vessel_description IS NOT NULL
GROUP BY 1
ORDER BY vessel_count DESC
