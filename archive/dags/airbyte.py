from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.operators.http import HttpOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
import requests

from airflow.operators.dummy import DummyOperator


def get_airbyte_token(**context):
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

    # Guardamos en XCom
    context["ti"].xcom_push(key="airbyte_token", value=f"Bearer {token}")


def inject_token(**context):
    ti = context["ti"]
    token = ti.xcom_pull(key="airbyte_token", task_ids="get_airbyte_token")
    trigger_sync.headers["Authorization"] = token


default_args = {
    "owner": "airflow",
    "retries": 1,
}

with DAG(
    dag_id="airbyte_sync_dag",
    default_args=default_args,
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
    tags=["airbyte"],
) as dag:

    start = DummyOperator(task_id="start")

    fetch_token = PythonOperator(
        task_id="get_airbyte_token",
        python_callable=get_airbyte_token,
        provide_context=True,
    )

    trigger_sync = HttpOperator(
        task_id="start_airbyte_sync",
        http_conn_id="airbyte_connection_test",  # conexión HTTP en Airflow
        endpoint="api/v1/connections/sync",
        method="POST",
        data='{"connectionId": "1631d942-dc3a-47ab-aa70-99a48f048c08"}',
        # headers={"Content-Type": "application/json"},
        headers={
            "Authorization": "{{ ti.xcom_pull(task_ids='get_airbyte_token', key='airbyte_token') }}",
            "Content-Type": "application/json",
        },
        response_check=lambda response: response.status_code == 200,
        log_response=True,
    )

    set_token = PythonOperator(
        task_id="inject_token",
        python_callable=inject_token,
        provide_context=True,
    )

    end = DummyOperator(task_id="end")

    # Flow
    start >> fetch_token >> set_token >> trigger_sync >> end
