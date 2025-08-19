select
        b.*,
        s.vessel_group as vessel_description,
        c.country as flag_country,
        -- Normalize and clean the destination field
        trim(upper(b.destination)) as destination_clean,

        -- Destination components for fallback matc
        split_part(trim(upper(b.destination)), ' ', 1) as dest_country_guess,
        split_part(trim(upper(b.destination)), ' ', 2) as dest_loc_guess

    from {{ ref('stg_joins') }} b
    left join {{ ref('ship_types') }} s
      on b.type = s.vessel_type
    left join {{ ref('mid_country') }} c
        on b.mid = c.mid

