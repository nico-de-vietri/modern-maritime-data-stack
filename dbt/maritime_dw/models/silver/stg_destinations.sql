{{ config(materialized='incremental', unique_key='unique_row_id') }}

    select
        unique_row_id,
        user_id,
        destination,
        -- ETA
        eta,
        nullif((eta->>'Month')::int, 0) as eta_month,
        nullif((eta->>'Day')::int, 0) as eta_day,
        nullif((eta->>'Hour')::int, 25) as eta_hour,
        nullif((eta->>'Minute')::int, 60) as eta_minute,
        {{ safe_eta_timestamp('eta') }} as eta_timestamp

        

    from {{ ref('bronze_destinations') }} 
    where destination is not null
    and (eta->>'Hour')::int between 0 and 24