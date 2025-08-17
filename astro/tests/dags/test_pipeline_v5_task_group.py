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
from airflow.utils.task_group import TaskGroup

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
    dag_id="maritime_pipeline_dbt_3",
    schedule_interval=timedelta(minutes=3),
    start_date=datetime(2025, 8, 1, tz="UTC"),
    catchup=False,
    tags=["maritime", "airbyte", "minio", "dbt"],
)
def pipeline_dbt():

    @task
    def api_to_minio():
        run_ingestion()

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

    # dbt tasks
    @task
    def bronze():
        os.system("dbt run --select bronze_clean")

    @task
    def bronze_test():
        os.system("dbt test --select bronze_clean")

    @task
    def seed():
        os.system("dbt seed")

    @task
    def silver():
        os.system("dbt run --select silver")

    @task
    def silver_test():
        os.system("dbt test --select silver")

    @task
    def gold():
        os.system("dbt run --select gold")

    @task
    def gold_test():
        os.system("dbt test --select gold")

    # pipeline flow
    # Extract
    with TaskGroup("extract", tooltip="Extract from API to Minio") as extract:
        api_to_minio_task = api_to_minio()
        token_task = fetch_token()

    # Load
    with TaskGroup("load", tooltip="Load data via Airbyte") as load:
        trigger_sync_task = trigger_sync(token_task)

    # Transform
    with TaskGroup("transform", tooltip="Transform data with DBT") as transform:
        bronze_task = bronze()
        bronze_test_task = bronze_test()
        seed_task = seed()
        silver_task = silver()
        silver_test_task = silver_test()
        gold_task = gold()
        gold_test_task = gold_test()

        (
            bronze_task
            >> [bronze_test_task, seed_task]
            >> silver_task
            >> silver_test_task
            >> gold_task
            >> gold_test_task
        )

    # Dependencies
    api_to_minio_task >> load
    token_task >> load
    load >> transform


pipeline_dbt()
