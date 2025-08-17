import requests

url = "http://airbyte-abctl-control-plane/a/v1/applications/token "  # "https://api.airbyte.com/v1/applications/token"

payload = {
    "client_id": "aecadebd-e47a-4986-af3e-dfa90b8166c1",
    "client_secret": "YWYrSncwIIdwDNx4NhNqVuWdof3upImx",
}
headers = {"accept": "application/json", "content-type": "application/json"}

response = requests.post(url, json=payload, headers=headers)

print(response.text)
