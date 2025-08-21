select *
from {{ silver }}
where eta_timestamp is not null
  and eta_timestamp::text !~ '^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
