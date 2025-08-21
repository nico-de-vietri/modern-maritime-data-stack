import requests


def get_token(airbyte_api_url, client_id, client_secret) -> str:
    url = f"{airbyte_api_url}/applications/token"
    payload = {"client_id": client_id, "client_secret": client_secret}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    token = response.json().get("access_token")
    if not token:
        raise Exception("access_token not found.")
    return f"Bearer {token}"
