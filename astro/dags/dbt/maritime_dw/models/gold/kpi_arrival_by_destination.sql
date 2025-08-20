{{ config(materialized='table') }}

WITH top_countries AS (
    SELECT
        destination_country,
        COUNT(DISTINCT unique_row_id) AS total_arrivals
    FROM {{ ref('gold') }}
    WHERE eta_date IS NOT NULL
      AND destination_country IS NOT NULL
      AND eta_date >= CURRENT_DATE - INTERVAL '3 months'
    GROUP BY destination_country
    ORDER BY total_arrivals DESC
    LIMIT 5
),

data_with_others AS (
    SELECT
        date_trunc('month', eta_date) AS eta_month,
        CASE
            WHEN destination_country IN (SELECT destination_country FROM top_countries) THEN destination_country
            ELSE 'Others'
        END AS destination_group,
        COUNT(DISTINCT unique_row_id) AS total_arrivals
    FROM {{ ref('gold') }}
    WHERE eta_date IS NOT NULL
      AND destination_country IS NOT NULL
      AND eta_date >= CURRENT_DATE - INTERVAL '3 months'
    GROUP BY 1, 2
)

SELECT
    eta_month,
    destination_group,
    total_arrivals
FROM data_with_others
ORDER BY eta_month DESC, total_arrivals DESC



