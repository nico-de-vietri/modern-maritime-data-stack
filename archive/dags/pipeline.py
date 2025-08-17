from airflow.decorators import dag, task
import pendulum
import requests
from include.main_api_to_minio import run_ingestion


@dag(
    dag_id="maritime_pipeline",
    schedule_interval="@hourly",
    start_date=pendulum.datetime(2025, 1, 8, tz="UTC"),
    catchup=False,
)
def pipeline():

    @task
    def api_to_minio():
        run_ingestion()

    @task
    def fetch_token() -> str:
        url = "http://airbyte-abctl-control-plane/api/v1/applications/token"
        client_id = "aecadebd-e47a-4986-af3e-dfa90b8166c1"
        client_secret = "YWYrSncwIIdwDNx4NhNqVuWdof3upImx"

        payload = {"client_id": client_id, "client_secret": client_secret}
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            raise Exception(
                f"Error al obtener token: {response.status_code}, {response.text}"
            )

        token = response.json().get("access_token")
        if not token:
            raise Exception("No se encontró access_token en la respuesta.")

        return f"Bearer {token}"

    @task
    def trigger_sync(token: str):
        url = "http://airbyte-abctl-control-plane/api/v1/connections/sync"
        headers = {"Authorization": token, "Content-Type": "application/json"}
        payload = {"connectionId": "1631d942-dc3a-47ab-aa70-99a48f048c08"}

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(
                f"Error al llamar Airbyte: {response.status_code}, {response.text}"
            )
        print("Sync triggered with response:", response.text)

    # Pipeline flow
    token = fetch_token()
    api_to_minio() >> trigger_sync(token)


pipeline()
