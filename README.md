Data Engineering Project ELT with Airflow, Airbyte, MinIO, Postgres, and dbt
Dockerfiles were customized accordingly to run and install dependencies
docker-compose.yaml ouside astro handles images from minio, postgres-destination(the data warehouse), dbt for local development and testing and superset
.env outside astro is being used for docker-compose.yaml
it is a bit untidy yet


EXTRACT – from API to Object Storage

This pipeline connects to a real-time AIS (Automatic Identification System) data stream via WebSocket, processes messages per ship, and stores them in MinIO.

Features

Real-time AIS data ingestion (Position, Static Data, Class B Reports)

Batch uploads of ship snapshots to MinIO (JSON Lines) to mimic batch processing, instead of streaming.

Individual event logging for traceability (just the bucket for the moment)

Automatic reconnection with exponential backoff, (by Airflows's default task params)

Per-ship message fusion for accurate state tracking (custom)

Airflow-ready for scheduling (e.g., every X minutes)

Folder Structure for API extract and first load into Minio

Folder Structure
astro/dags/include/
├── ais_websocket.py                          # WebSocket connection and message processing
├── minio_client.py                           # MinIO client and bucket setup
├── minio_utils.py                            # Utilities for naming and uploading objects
├── main_api_to_minio_snapshot_and_events.py  # Main ingestion logic
├── airbyte_token_utils.py                    # gets new Airbyte token
├── airbyte_utils.py                          # custom Airbyte sync trigger 

How it Works

Connect to AIS WebSocket

Endpoint: wss://stream.aisstream.io/v0/stream

Subscribes to [-90, -180] to [90, 180] (whole world)

Filters message types:

PositionReport

ShipStaticData

StandardClassBPositionReport

LongRangeAisBroadcastMessage

Fuse Messages by Ship

Group incoming messages by UserID

Maintain per-ship snapshot of latest known data

Process & Upload

Add snapshots to batch; upload to MinIO on batch size/timeout

Store individual events as single JSON files (append-only)

MinIO Buckets
Bucket Name	Description
MINIO_BUCKET	Batched snapshots (JSON Lines)
MINIO_BUCKET_EVENTS	Individual event logs (single JSON)

Airflow DAG:
run_ingestion() connects to the AIS stream, listens for a configurable time (default 30s), batches/uploads data, and exits.
Recommended Airflow schedule: every 3 minutes.

Example Log Output:
Message Received Type: StandardClassBPositionReport
Processing Ship ID: 261002981
Uploaded batch position_report_20250815T090045603654_654f24.json with 58 records

Error Handling:

Retries with exponential backoff 

Max retries: x (configurable)

Handles dropped connections & JSON parsing errors


LOAD – from MinIO to Data Warehouse

Airbyte loads data from MinIO into Postgres.
A custom Python function:

Fetches a valid OAuth2 token

Waits for any ongoing sync to finish

Triggers a new sync and polls until completion

This method offers more control over authentication, retries, and job tracking than the standard AirbyteTriggerSyncOperator in the current setup.

set up source type minio and destination type postgres
create connection
get conn_id for .env see url connections/
http://localhost:8000/workspaces/97b1302c-3e1e-4ff0-8479-4051ac35d58a/connections/1631d942-dc3a-47ab-aa70-99a48f048c08/status
connection settings
sync>manual: Airflow will trigger it
schema sync mode incremental append + deduped PK UserID

TRANSFORM – modeling for consumption

dbt: transformations and modeling in Postgres
3 Layer > bronze_clean , silver, gold
.csv to enrich data

Superset: dashboards and visualization
ongoing














Data Engineering Project with Airflow, Airbyte, MinIO, Postgres, and dbt


EXTRACT PART from API

This pipeline connects to a real-time AIS (Automatic Identification System) data stream via WebSocket, processes messages per ship, and stores the data efficiently in MinIO.

Features

Real-time AIS data ingestion (Position, Static Data, Class B Reports)

Batch uploads of ship snapshots to MinIO (as JSON Lines)

Individual event logging for detailed traceability

Automatic reconnection with exponential backoff

Per-ship message fusion for accurate state tracking

Works well with Airflow DAGs (e.g., every x mins)

Folder Structure
astro/dags/include/
├── ais_websocket.py                          # WebSocket connection and message processing
├── minio_client.py                           # MinIO client and bucket setup
├── minio_utils.py                            # Utilities for naming and uploading objects
├── main_api_to_minio_snapshot_and_events.py  # Main ingestion logic
├── airbyte_token_utils.py                    # gets new Airbyte token
├── airbyte_utils.py                          # custom Airbyte sync trigger 

How it Works
Connect to AIS WebSocket

Endpoint: wss://stream.aisstream.io/v0/stream

Subscribes to global bounding box ([-90, -180] to [90, 180])

Filters for message types:

PositionReport

ShipStaticData

StandardClassBPositionReport

LongRangeAisBroadcastMessage

Fuse Messages by Ship

Incoming messages are grouped and updated by UserID (ship identifier)

This creates a per-ship snapshot of the latest known data

Process and Upload

The ingestion logic does two things per message:

Add the snapshot to a batch and upload to MinIO once batch size or timeout is met

Upload the individual event as a single JSON file (append-only)

Storage in MinIO

Data is stored in two separate buckets:

Bucket Name	Description
MINIO_BUCKET	Batched snapshots (JSON Lines)
MINIO_BUCKET_EVENTS	Individual event logs (single JSON files)

Object names are timestamped for uniqueness.

Environment Variables

These should be defined in a .env file at the root of the project:

AIS_API_KEY=your_ais_api_key
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minio_access_key
MINIO_SECRET_KEY=minio_secret_key
MINIO_BUCKET=ais-snapshots
MINIO_BUCKET_EVENTS=ais-events

Usage
Run the ingestion triggered by Airflow
python main_api_to_minio_snapshot_and_events.py

Use in Airflow DAG:

The run_ingestion() function is designed to be run inside an Airflow task. It:

Connects to the AIS stream

Listens for 30 seconds (configurable)

Handles batching and uploading

Then exits, ready for the next scheduled run

Airflow can be set to run this every 3 minutes, for example.

Example Output

In logs:

📡 Messaged Received Type: StandardClassBPositionReport
Processing menssage Ship ID: 261002981
Uploaded batch position_report_20250815T090045603654_654f24.json with 58 records (JSON Lines)

Error Handling & Retries

If WebSocket fails, it retries with exponential backoff (2^retries seconds).

Max retries: 5 (configurable)

It handles dropped connections and JSON parsing errors

Future Improvements

Add metrics for monitoring

Retry failed uploads to MinIO

Add retention policy / lifecycle rules for stored data




LOAD PART to DATAWAREHOUSE

Airbyte: Handles data extraction from minio to postgres and loading, running locally via abctl.
custom Python function was created to:
Fetch a valid OAuth2 token
Wait for any currently running sync to finish
Trigger a new sync
Poll and wait for the job to complete
This approach offers full control over authentication, retries, and job status tracking, and has proven more reliable within this specific setup.
In a future environment using a standard Airbyte deployment with basic auth (or no auth), the official AirbyteTriggerSyncOperator could be reintroduced for cleaner DAG code and tighter integration.

MinIO: Provides S3-compatible object storage for raw data.
Postgres: Acts as the destination data warehouse.

TRANSFORM PART modeling for consume
dbt: Performs data transformations and modeling on the data warehouse.
superset: for visuals
The architecture consists of three main blocks:


Astro CLI running Airflow, the nervous system of the data pipeline orchestrating tasks.
Aiflow gets data from the API and stores is minio. the Extract part
Airbyte running locally (outside Docker Compose) for ingestion. The Load part
Docker Compose environment running MinIO, Postgres, and also dbt for local development before integration in astro project.
Components
Airbyte
Runs locally via abctl.
Connects to sources and destinations.
Uses service names (e.g., minio:9000) to communicate within Docker network.
Airflow (Astro CLI)
Runs outside Docker Compose.
Orchestrates ETL jobs and DAGs.
Uses environment variables from .env.
Requires restarting when .env values like IP addresses change.
Docker Compose
Contains:

MinIO (object storage on port 9000)
Postgres (data warehouse on port 4000)
dbt (transformation container)
All services are attached to an external Docker network named airbyte-net for cross-container communication.

Setup Instructions
Requirements
Python 3.11 or superior
git
macOS, Linux, o Windows (with WSL)
Docker
abctl local
astro cli

Instalation
Clone repo:
git clone https://github.com/tu_usuario/modern-maritime-data-stack.git
cd modern-maritime-data-stack

GET API KEY:

https://aisstream.io/authenticate?#

in astro/.env
AIS_API_KEY=your_api_key_here

Execute config script:

chmod +x setup.sh
./setup.sh

This will create a virtual environment to install requirements, etc, to isolate the system and not to touch the Python global system, to make it portable in other machines(?) and being consistent with good practices of software development.

Architecture diagram:

Próximamente: DAGs en Airflow, transformaciones con DBT, dashboards en Superset.

License

This is an educational project under MIT license. See LICENSE.

Author
@nico-de-vietri



