
--Systematically reject invalid dates
{% macro safe_eta_timestamp(eta_json) %}
    case 
        -- Handle invalid Feb 29 in non-leap years
        when nullif(({{ eta_json }} ->> 'Month')::int, 0) = 2
         and nullif(({{ eta_json }} ->> 'Day')::int, 0) = 29
         and not (
            extract(year from now())::int % 400 = 0 or
            (extract(year from now())::int % 4 = 0 and extract(year from now())::int % 100 != 0)        
         )
        then null

        -- Handle invalid day for each month (e.g., Nov 31)
        when (
            ({{ eta_json }} ->> 'Month')::int = 4 and ({{ eta_json }} ->> 'Day')::int > 30
         ) or (
            ({{ eta_json }} ->> 'Month')::int = 6 and ({{ eta_json }} ->> 'Day')::int > 30
         ) or (
            ({{ eta_json }} ->> 'Month')::int = 9 and ({{ eta_json }} ->> 'Day')::int > 30
         ) or (
            ({{ eta_json }} ->> 'Month')::int = 11 and ({{ eta_json }} ->> 'Day')::int > 30
         ) or (
            ({{ eta_json }} ->> 'Month')::int in (1,3,5,7,8,10,12) and ({{ eta_json }} ->> 'Day')::int > 31
         )
        then null

        -- Build timestamp only if all parts are valid
        when nullif(({{ eta_json }} ->> 'Month')::int, 0) is not null
         and nullif(({{ eta_json }} ->> 'Day')::int, 0) is not null
         and nullif(({{ eta_json }} ->> 'Hour')::int, 25) is not null
         and nullif(({{ eta_json }} ->> 'Minute')::int, 60) is not null
        then
            make_timestamp(
                extract(year from now())::int,
                ({{ eta_json }} ->> 'Month')::int,
                ({{ eta_json }} ->> 'Day')::int,
                ({{ eta_json }} ->> 'Hour')::int,
                ({{ eta_json }} ->> 'Minute')::int,
                0
            )
        else null
    end
{% endmacro %}
