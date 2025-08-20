{{ config(materialized='table') }}

with base as (
  select * from {{ ref('gold') }}
),

totals as (
  select count(*) as total_rows from base
),

nulls_per_column as (
  select
    'speed_over_ground_knots' as column_name,
    count(*) filter (where speed_over_ground_knots is null) as null_count
  from base

  union all

  select
    'dimension_length_meters',
    count(*) filter (where dimension_length_meters is null)
  from base

  union all

  select
    'dimension_width_meters',
    count(*) filter (where dimension_width_meters is null)
  from base

  union all

  select
    'eta_date',
    count(*) filter (where eta_date is null)
  from base

  union all

  select
    'destination_country',
    count(*) filter (where destination_country is null)
  from base

  union all

  select
    'latitude',
    count(*) filter (where latitude is null)
  from base

  union all

  select
    'longitude',
    count(*) filter (where longitude is null)
  from base
)

select
  column_name,
  null_count,
  t.total_rows,
  round(100.0 * null_count / nullif(t.total_rows, 0), 2) as null_percentage
from nulls_per_column, totals t
order by null_percentage desc
