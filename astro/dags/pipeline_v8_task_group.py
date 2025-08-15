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
from include.airbyte_token_utils import get_token
import subprocess
import logging

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
    dag_id="maritime_pipeline_dbt_6",
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

        # task wrapper needs to return taskinstance can be used downstream
        return api_to_minio()

    @task_group(group_id="load")
    def load_group():
        @task
        def fetch_token():
            # task wrapper needs to return so can be used downstream
            return get_token(AIRBYTE_API_URL, CLIENT_ID, CLIENT_SECRET)

        @task(
            retries=3,  # number of retries
            retry_delay=timedelta(seconds=60),  # wait 60 seconds between retries
            retry_exponential_backoff=True,
        )
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
        @task
        def dbt_build_model(model: str):
            logging.info(f"Starting dbt build for model: {model}")
            try:
                # Run dbt build for the given model
                subprocess.run(
                    ["dbt", "build", "--select", model],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                logging.info(f"dbt build succeeded for model: {model}")
            except subprocess.CalledProcessError as e:
                logging.error(f"dbt build failed for model: {model}")
                logging.error(f"stdout: {e.stdout}")
                logging.error(f"stderr: {e.stderr}")
                raise

        # Define tasks for each model
        bronze = dbt_build_model("bronze")
        silver = dbt_build_model("silver")
        gold = dbt_build_model("gold")

        # Set dependencies
        bronze >> silver >> gold

    api_task = extract_group()
    token_task, sync_task = load_group()
    transform_task = transform_group()

    api_task >> token_task >> sync_task >> transform_task


pipeline_dbt()
