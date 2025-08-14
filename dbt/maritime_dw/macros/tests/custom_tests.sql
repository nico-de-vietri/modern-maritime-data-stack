{% test valid_eta_timestamp(model, column_name) %}
select *
from {{ model }}
where {{ column_name }} is not null
  and (
    extract(hour from {{ column_name }}) not between 0 and 23
    or extract(minute from {{ column_name }}) not between 0 and 59
  )
{% endtest %}
