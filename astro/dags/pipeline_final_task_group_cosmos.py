import os
import time
import requests
from airflow.decorators import dag, task, task_group
from pendulum import datetime
from datetime import timedelta
from include.main_api_to_minio_snapshot_and_events import run_ingestion
from dotenv import load_dotenv
from cosmos import (
    DbtTaskGroup,
    ProjectConfig,
    ProfileConfig,
    RenderConfig,
    ExecutionConfig,
)
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
DBT_DIR = os.getenv("DBT_PROJECT_DIR", "/usr/local/airflow/dags/dbt/maritime_dw")


@dag(
    dag_id="maritime_pipeline_ais_api",
    max_active_runs=1,
    schedule=timedelta(minutes=30),
    start_date=datetime(2025, 8, 1, tz="UTC"),
    catchup=False,  # dont think it works well with catchup=True because of the API
    tags=["ais-api", "airbyte", "minio", "dbt"],
)
def pipeline_elt():

    @task
    def check_env_vars():
        assert (
            AIRBYTE_API_URL and CLIENT_ID and CLIENT_SECRET and CONNECTION_ID
        ), "Required environmental variables missing: check .env file."

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
                check_interval=30,  # this one here could be ommited, because we have retry_delay, to be tested.
            )

        token = fetch_token()
        sync = trigger_sync(token)
        # task wrapper needs to return so can be used downstream
        return token, sync

    dbt_task_group = DbtTaskGroup(
        group_id="transform",
        project_config=ProjectConfig(DBT_DIR),
        profile_config=ProfileConfig(
            profile_name="maritime_dw",
            target_name="dev",
            profile_mapping=PostgresUserPasswordProfileMapping(
                conn_id="my_postgres_conn",  # var set in airflow
                profile_args={
                    "dbname": os.getenv("POSTGRES_DESTINATION_DB_NAME", "postgres"),
                    "schema": "public",
                },
            ),
        ),
        render_config=RenderConfig(
            select=["*"]
        ),  # or ["bronze_clean", "silver", "gold"]
        execution_config=ExecutionConfig(
            dbt_executable_path="/usr/local/airflow/dbt_venv/bin/dbt"
        ),
    )
    check_env = check_env_vars()
    extract = extract_group()
    token, sync = load_group()

    check_env >> extract >> token >> sync >> dbt_task_group


pipeline_elt()
