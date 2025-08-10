SELECT
  "UserID",
  "Eta",
  NULLIF(("Eta"->>'Month')::int, 0) as month_raw,
  NULLIF(("Eta"->>'Day')::int, 0) as day_raw,
  ("Eta"->>'Hour')::int as hour_raw,
  ("Eta"->>'Minute')::int as minute_raw,

  CASE 
    WHEN NULLIF(("Eta"->>'Month')::int, 0) IS NOT NULL
     AND NULLIF(("Eta"->>'Day')::int, 0) IS NOT NULL
    THEN
      make_timestamp(
        extract(year from now())::int,
        ("Eta"->>'Month')::int,
        ("Eta"->>'Day')::int,
        CASE WHEN ("Eta"->>'Hour')::int = 24 THEN 0 ELSE ("Eta"->>'Hour')::int END,
        CASE WHEN ("Eta"->>'Minute')::int = 60 THEN 0 ELSE ("Eta"->>'Minute')::int END,
        0
      ) + 
      CASE WHEN ("Eta"->>'Hour')::int = 24 THEN interval '1 day' ELSE interval '0' END
    ELSE
      NULL
  END AS eta_timestamp
FROM public.bronze_clean
WHERE "Eta" IS NOT NULL
LIMIT 100;