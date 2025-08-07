from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import asyncio
import os
import sys
import json

# Asegurate de que esta ruta apunte a donde están los módulos copiados
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from include.main_api_to_minio import run_ingestion
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator
from airflow.providers.airbyte.sensors.airbyte import AirbyteJobSensor
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.models import Variable, Connection
from include.airbyte_token import get_airbyte_token, inject_token_pre_execute


AIRBYTE_CONN_ID = Variable.get("AIRBYTE_CONN_ID")

API_KEY = f'Bearer {Variable.get("API_AIRBYTE_TOKEN")}'


default_args = {
    "owner": "nico",
    "depends_on_past": False,
    "start_date": datetime(2025, 7, 25),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="ingest_to_minio",
    default_args=default_args,
    description="Ingesta AIS desde websocket a MinIO por batches",
    schedule_interval="@hourly",
    catchup=False,
    tags=["ais", "minio", "websocket"],
) as dag:

    task_ingest = PythonOperator(
        task_id="task_ingest",
        python_callable=run_ingestion,
    )

    # sync_airbyte = AirbyteTriggerSyncOperator(
    #     task_id="sync_airbyte",
    #     airbyte_conn_id="airbyte_connection",  # Connection ID en Airflow
    #     connection_id="1631d942-dc3a-47ab-aa70-99a48f048c08",  # Airbyte conn ID
    #     asynchronous=False,
    #     timeout=3600,
    #     wait_seconds=10,
    # )
    # sync_airbyte = AirbyteTriggerSyncOperator(
    #     task_id="sync_airbyte",
    #     airbyte_conn_id="airbyte-provider",  # debe coincidir con la conexión Airflow
    #     connection_id="1631d942-dc3a-47ab-aa70-99a48f048c08",
    #     asynchronous=True,
    #     timeout=3600,
    #     wait_seconds=10,
    # )

    # sensor_airbyte = AirbyteJobSensor(
    #     task_id="sensor_airbyte",
    #     airbyte_conn_id="airbyte_connection",
    #     airbyte_job_id=sync_airbyte.output,
    # )

    # # task_ingest >>
    # sync_airbyte >> sensor_airbyte

    trigger_sync = HttpOperator(
        task_id="start_airbyte_sync",
        http_conn_id="airbyte_connection_test",
        endpoint="/api/v1/connections/sync",
        method="POST",
        data='{"connectionId": "1631d942-dc3a-47ab-aa70-99a48f048c08"}',
        # headers={"Content-Type": "application/json"},
        headers={
            "Content-Type": "application/json",
            "Authorization": "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vYWlyYnl0ZS1hYmN0bC1haXJieXRlLXdlYmFwcC1zdmM6ODAiLCJhdWQiOiJhaXJieXRlLXNlcnZlciIsInN1YiI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsImV4cCI6MTc1Mzk5MjI0Mywicm9sZXMiOlsiQVVUSEVOVElDQVRFRF9VU0VSIiwiUkVBREVSIiwiRURJVE9SIiwiQURNSU4iLCJPUkdBTklaQVRJT05fTUVNQkVSIiwiT1JHQU5JWkFUSU9OX1JFQURFUiIsIk9SR0FOSVpBVElPTl9SVU5ORVIiLCJPUkdBTklaQVRJT05fRURJVE9SIiwiT1JHQU5JWkFUSU9OX0FETUlOIiwiV09SS1NQQUNFX1JFQURFUiIsIldPUktTUEFDRV9SVU5ORVIiLCJXT1JLU1BBQ0VfRURJVE9SIiwiV09SS1NQQUNFX0FETUlOIl19.vOCS3cktBYzF4o0moStvq9Vfrdfgblpq2AcWTk6X0Z8",  # <- AGREGALO AQUÍ
        },
        # headers={},
        # pre_execute=inject_token_pre_execute,
        log_response=True,
    )
    task_ingest >> trigger_sync
    # task_ingest >> sync_airbyte
