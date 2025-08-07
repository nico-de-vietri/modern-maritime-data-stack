import requests
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
EMAIL = os.getenv("AIRBYTE_EMAIL")
PASSWORD = os.getenv("AIRBYTE_PASSWORD")

import requests


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
