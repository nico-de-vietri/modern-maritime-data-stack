import time
import requests


def trigger_airbyte_sync(
    airbyte_api_url,
    connection_id,
    token,
    max_wait_seconds=120,
    check_interval=30,
):

    waited = 0

    headers = {"Authorization": token, "Content-Type": "application/json"}
    payload = {"connectionId": connection_id}

    # checks if airbyte sync is runnig , if running wait MAX_WAIT_SECONDS
    # recheck every CHECK_INTERVAL if its free
    status_url = f"{airbyte_api_url}/connections/get"
    while True:
        status_resp = requests.post(status_url, headers=headers, json=payload)
        status_resp.raise_for_status()

        job_status = status_resp.json().get("latestSyncJobStatus", "").lower()
        print(f"Airbyte sync status: {job_status}")

        if job_status not in ("running", "pending"):
            break

        if waited >= max_wait_seconds:
            raise TimeoutError(
                f"Airbyte sync is still running after {max_wait_seconds//60} minutes."
            )

        print(f"Sync running. Waiting {check_interval} seconds...")
        time.sleep(check_interval)
        waited += check_interval

    # trigger sync
    sync_url = f"{airbyte_api_url}/connections/sync"
    sync_resp = requests.post(sync_url, headers=headers, json=payload)
    sync_resp.raise_for_status()
    job_id = sync_resp.json()["job"]["id"]
    print(f"Triggered Airbyte job ID: {job_id}")

    # Wait for sync job to complete
    job_url = f"{airbyte_api_url}/jobs/get"
    job_payload = {"id": job_id}
    print(f"Triggered Airbyte job ID: {job_id}")

    while max_wait_seconds > 0:
        job_resp = requests.post(job_url, headers=headers, json=job_payload)
        job_resp.raise_for_status()
        job_status = job_resp.json()["job"]["status"].lower()

        print(f"Airbyte job status: {job_status}")
        if job_status in ("succeeded", "failed", "cancelled"):
            break

        time.sleep(check_interval)
        max_wait_seconds -= check_interval

    if job_status != "succeeded":
        raise Exception(f"Airbyte job {job_id} failed with status: {job_status}")
    print(f"Airbyte sync job {job_id} completed successfully.")


# token


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
