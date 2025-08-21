{{ config(materialized='incremental', unique_key='unique_row_id') }}
    select
        unique_row_id,
        user_id,
        navigational_status::int
        

    from  {{ ref('bronze_status') }}