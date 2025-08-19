{{ config(
    materialized = 'incremental',
    unique_key = 'unique_row_id'
) }}

with silver as(


    select
        e.*,
        nv1.description as navigation_status,
        coalesce(
            p1.country_code, 
            p2.country_code
        ) as destination_country,
        cc1.country_name,
        coalesce(
            p1.port_name,
            p2.port_name
        ) as matched_port,
        coalesce(p1.latitude_destination, p2.latitude_destination) as latitude_destination,
        coalesce(p1.longitude_destination, p2.longitude_destination) as longitude_destination

    from {{ ref('silver_enriched') }} e

    -- Primary match on cleaned destination name
    left join {{ ref('ports') }} p1
        on e.destination_clean = p1.port_name

    -- Fallback: match on country & location code
    left join {{ ref('ports') }} p2
        on e.dest_country_guess = p2.country_code
        and e.dest_loc_guess = p2.location_code
    left join {{ ref('country_code') }} cc1
        on p1.country_code=cc1.country_code
    left join {{ ref('navigation_status') }} nv1
        on e.navigational_status=nv1.navigation_status
)

select * 
from silver
{% if is_incremental() %}
where _airbyte_extracted_at > (select coalesce(max(_airbyte_extracted_at), '1900-01-01'::timestamp) FROM {{ this }})
{% endif %}
