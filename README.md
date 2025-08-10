Data Engineering Project with Airflow, Airbyte, MinIO, Postgres, and dbt
Overview
This project demonstrates a data engineering pipeline composed of several components:


Datasource API [AISStream.io](https://aisstream.io)
Airflow: Orchestrates the data workflows, running on Astro CLI.
Airbyte: Handles data extraction and loading, running locally via abctl.
MinIO: Provides S3-compatible object storage for raw data.
Postgres: Acts as the destination data warehouse.
dbt: Performs data transformations and modeling on the data warehouse.
The architecture consists of three main blocks:

Airbyte running locally (outside Docker Compose) for ingestion.
Astro CLI running Airflow, orchestrating tasks.
Docker Compose environment running MinIO, Postgres, and dbt.
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
⚙️ Requirements
Python 3.8 or superior
git
macOS, Linux, o Windows (with WSL)
Docker
abctl local
astro cli

Instalation
Clona el repositorio:
git clone https://github.com/tu_usuario/modern-maritime-data-stack.git
cd modern-maritime-data-stack

    Crea un archivo .env en la root del proyecto con tu clave API:
Logeate con Github para obtener tu API KEY
https://aisstream.io/authenticate?#

AIS_API_KEY=tu_api_key_aqui

    Ejecuta el script de configuración:

chmod +x setup.sh
./setup.sh

Esto hará:

    Crear un entorno virtual, para aislar el sistema y no instalar paquetes en el sistema global de Python, poder replicarlo en otra maquina (portabilidad) y buenas prácticas

    Activarlo

    Instalar dependencias

Uso

Desde la root del proyecto, activa el entorno y ejecuta el colector:

source venv/bin/activate
python data_collector/main.py

Próximamente: DAGs en Airflow, transformaciones con DBT, dashboards en Superset.
Licencia

Este proyecto está bajo la licencia MIT. Ver archivo LICENSE.

Autor
@nico-de-vietri



