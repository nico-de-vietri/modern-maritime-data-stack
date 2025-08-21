{{ config(materialized='table') }}

WITH points AS (
  SELECT
    ST_SetSRID(ST_MakePoint(longitude, latitude), 4326) AS geom
  FROM {{ ref('gold') }}
  WHERE latitude IS NOT NULL AND longitude IS NOT NULL
),

grid AS (
  SELECT
    ST_SnapToGrid(geom, 0.1) AS grid_cell
  FROM points
)

SELECT
  grid_cell,
  COUNT(*) AS vessel_count,
  ST_X(grid_cell) AS lon_rounded,
  ST_Y(grid_cell) AS lat_rounded
FROM grid
GROUP BY grid_cell
ORDER BY vessel_count DESC

