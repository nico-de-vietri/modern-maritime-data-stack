import os
import time
import requests
from airflow.decorators import dag, task
from pendulum import datetime
from datetime import timedelta
from include.main_api_to_minio_snapshot_and_events import run_ingestion
from dotenv import load_dotenv
from cosmos import DbtDag, ProjectConfig, ProfileConfig, RenderConfig, ExecutionConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping

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
    dag_id="maritime_pipeline_dbt",
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

        MAX_WAIT_SECONDS = 600
        CHECK_INTERVAL = 30
        waited = 0

        status_url = f"{AIRBYTE_API_URL}/connections/get"
        sync_url = f"{AIRBYTE_API_URL}/connections/sync"
        headers = {"Authorization": token, "Content-Type": "application/json"}
        payload = {"connectionId": CONNECTION_ID}

        # checks if airbyte sync is runnig , if running wait MAX_WAIT_SECONDS
        # recheck every CHECK_INTERVAL if its free
        while True:
            status_resp = requests.post(status_url, headers=headers, json=payload)
            status_resp.raise_for_status()

            job_status = status_resp.json().get("latestSyncJobStatus", "").lower()
            print(f"Airbyte sync status: {job_status}")

            if job_status not in ("running", "pending"):
                break

            if waited >= MAX_WAIT_SECONDS:
                raise TimeoutError(
                    f"Airbyte sync is still running after {MAX_WAIT_SECONDS/60} minutes."
                )

            print(f"Sync running. Waiting {CHECK_INTERVAL} seconds...")
            time.sleep(CHECK_INTERVAL)
            waited += CHECK_INTERVAL

        response = requests.post(sync_url, headers=headers, json=payload)
        response.raise_for_status()
        print("Sync triggered with response:", response.text)

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
    token = fetch_token()
    (
        api_to_minio()
        >> trigger_sync(token)
        >> bronze()
        >> [bronze_test(), seed()]
        >> silver()
        >> silver_test()
        >> gold()
        >> gold_test()
    )


pipeline_dbt()
