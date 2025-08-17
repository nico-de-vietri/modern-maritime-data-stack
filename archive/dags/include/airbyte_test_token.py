import requests
from airflow.models import Variable


def get_airbyte_token(**kwargs):
    url = "http://airbyte-abctl-control-plane/api/oauth/token"  # o el correcto si es diferente
    client_id = "aecadebd-e47a-4986-af3e-dfa90b8166c1"
    client_secret = "YWYrSncwIIdwDNx4NhNqVuWdof3upImx"

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }

    response = requests.post(url, json=payload)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            f"Error al obtener token: {response.status_code}, {response.text}"
        )

    token = response.json().get("access_token")
    if not token:
        raise Exception("No se encontró access_token en la respuesta.")

    # Guardamos en XCom para que lo lea el HttpOperator
    kwargs["ti"].xcom_push(key="airbyte_token", value=f"Bearer {token}")
    print(token)
