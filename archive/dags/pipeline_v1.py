from airflow.decorators import dag, task
import pendulum
import requests
from include.main_api_to_minio import run_ingestion
from dotenv import load_dotenv
import os

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
    dag_id="maritime_pipeline",
    schedule_interval="@hourly",
    start_date=pendulum.datetime(2025, 1, 8, tz="UTC"),
    catchup=False,
    tags=["maritime", "airbyte", "minio"],
)
def pipeline_v1():

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
        url = f"{AIRBYTE_API_URL}/connections/sync"
        headers = {"Authorization": token, "Content-Type": "application/json"}
        payload = {"connectionId": CONNECTION_ID}

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("Sync triggered with response:", response.text)

    # pipeline flow
    token = fetch_token()
    api_to_minio() >> trigger_sync(token)


pipeline_v1()
