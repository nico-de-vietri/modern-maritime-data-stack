# superset
SQLAlchemy URI
postgresql+psycopg2://postgres:posgresadmin@postgres-destination:5432/postgres

# docker
docker ps
docker ps -a
docker network inspect airbyte-net (network-name)

# logins
-pgadmin:http://localhost:9081/browser/
-airbyte:http://localhost:8000/login --> abctl local credentials # to get your credentials
-airflow:http://localhost:8080
-minio:http://localhost:9001
-dbt:

# astro
astro dev run dags reserialize 
astro dev bash


# check .env and update new ips everywhere
.env
airbyte sources/destination
pgadmin
astro dev stop
astro dev restart

# reconnect containers to network (or whichever container name that needs to be in the same network)
docker network connect airbyte-net astro_ad7a2b-webserver-1
docker network connect airbyte-net astro_ad7a2b-triggerer-1
docker network connect airbyte-net astro_ad7a2b-scheduler-1
-------docker network connect airbyte-net astro_ad7a2b-postgres-1----- metadata db no need

# DW container minio-postgres-dbt
docker compose up -d
    # individual services
    docker compose up dbt -d