{{ config(materialized='incremental', unique_key='unique_row_id') }}
    select
        m.unique_row_id,
        m.user_id,
        s.name,
        p.latitude,
        p.longitude,
        p.speed_over_ground,
        p.course_over_ground,
        st.navigational_status,
        d.destination,
        s.dimension_length,
        s.dimension_width,
        m.mid,
        
        -- ETA
        d.eta,
        d.eta_month,
        d.eta_day,
        d.eta_hour,
        d.eta_minute,
        d.eta_timestamp,

        s.type,
        s.imo_number,
        m._airbyte_extracted_at

    from {{ ref('stg_messages') }} m
    left join {{ ref('stg_positions') }} p on m.user_id=p.user_id
    left join {{ ref('stg_ships') }} s on  m.user_id = s.user_id
    left join {{ ref('stg_status') }} st on m.user_id=st.user_id
    left join {{ ref('stg_destinations') }} d on m.user_id=d.user_id
    --where s.name is not null and d.eta is not null and d.destination is not null
    --and (d.eta->>'Hour')::int BETWEEN 0 AND 24