import os
import time
import requests
from airflow.decorators import dag, task, task_group
from pendulum import datetime
from datetime import timedelta
from include.main_api_to_minio_snapshot_and_events import run_ingestion
from dotenv import load_dotenv
from cosmos import DbtDag, ProjectConfig, ProfileConfig, RenderConfig, ExecutionConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping
from include.airbyte_utils import trigger_airbyte_sync


# load env vars from .env, please check .env and adjust if necessary
load_dotenv()

AIRBYTE_API_URL = os.getenv("AIRBYTE_API_URL")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CONNECTION_ID = os.getenv("AIRBYTE_CONNECTION_ID")

assert (
    AIRBYTE_API_URL and CLIENT_ID and CLIENT_SECRET and CONNECTION_ID
), "required environmental variables missing requeridas: check .env file."


@dag(
    dag_id="maritime_pipeline_dbt_4",
    schedule_interval=timedelta(minutes=3),
    start_date=datetime(2025, 8, 1, tz="UTC"),
    catchup=False,
    tags=["maritime", "airbyte", "minio", "dbt"],
)
def pipeline_dbt():

    @task_group(group_id="extract")
    def extract_group():
        @task
        def api_to_minio():
            run_ingestion()

        return api_to_minio()

    @task_group(group_id="load")
    def load_group():
        @task
        def fetch_token() -> str:
            url = f"{AIRBYTE_API_URL}/applications/token"
            payload = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}
            headers = {"Content-Type": "application/json"}

            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            token = response.json().get("access_token")
            if not token:
                raise Exception("access_token not found.")
            return f"Bearer {token}"

        @task
        def trigger_sync(token: str):
            trigger_airbyte_sync(
                airbyte_api_url=AIRBYTE_API_URL,
                connection_id=CONNECTION_ID,
                token=token,
                max_wait_seconds=120,
                check_interval=30,
            )

        token = fetch_token()
        sync = trigger_sync(token)
        return token, sync

    @task_group(group_id="transform")
    def transform_group():
        # dbt tasks
        @task
        def dbt_build(model: str):
            os.system(f"dbt build --select {model}")

        # Sequential dbt tasks not in //
        bronze = dbt_build.override(task_id="bronze")("bronze_clean")
        silver = dbt_build.override(task_id="silver")("silver")
        gold = dbt_build.override(task_id="gold")("gold")
        bronze >> silver >> gold

    api_task = extract_group()
    token_task, sync_task = load_group()
    transform_task = transform_group()

    api_task >> token_task >> sync_task >> transform_task


pipeline_dbt()
