# Lessons Learned

## Project Setup and Architecture

- Decidí separar Airbyte, Airflow (Astro CLI) y los servicios de infraestructura (MinIO, Postgres, dbt) en bloques separados para mantener cada componente independiente y facilitar debugging.
- Montar volumenes en Docker Compose para los proyectos de dbt facilita el desarrollo local y evitar rebuilds constantes.
- Usar `docker exec` para entrar en contenedores individuales y probar comandos agiliza el desarrollo.
- Variables sensibles se manejan mejor con archivos `.env` para no hardcodearlas en configuraciones ni código.

## Airbyte
Initially tried using the AirbyteTriggerSyncOperator from the Airflow Airbyte provider, but I was running Airbyte locally via abctl with a Kubernetes backend (provider kind), and it wasn't compatible out-of-the-box with the provider's expectations (like using basic auth or no auth). I also had to implement token-based authentication using the OAuth2 client credentials flow, which isn't supported by the standard operator. Because of this, I implemented a custom sync trigger function that handles both the token refresh and sync logic, and that ended up being more flexible and reliable in my setup.

AirbyteTriggerSyncOperator assumes that:

-Airbyte is accessible via a REST API

-No token-based auth is needed

-The connection is already configured and working

Using Airbyte’s default Docker-based deployment or Cloud

In this case running Airbyte via abctl + Kubernetes + kind provider (non-default setup)

- Airbyte API is protected by an OAuth2 token (non-standard for Airbyte deployments)

- The operator does not support fetching or injecting tokens

- Must handle token expiration/refresh and status polling manually

- Fine-grained control to debug and understand what's going on

- Basics to configure network and periodically check and update dynamic IPs of each service in the config

- If a sync is still running and there is another dag run, the sync task in Airflow will fail.

- With this kind of customs DIY solutions, Aibyte connection (or whichever service) could fail and still the dag runs successfully if you are not checking Airbyte job's status.

## Airflow & Astro CLI

- Ejecutar Airflow con Astro CLI es cómodo y está separado del resto de servicios, pero puede complicar la sincronización con otros contenedores en la red Docker.
- En un proyecto futuro podría experimentar corriendo Airflow también con Docker Compose para mayor integración.

## dbt

- Es fundamental iniciar el proyecto dbt temprano y definir bien los modelos antes de integrarlo en el pipeline.
- Usar Docker para dbt con montajes de volumen es ideal para sincronizar código y facilitar iteraciones.
- La instalación de dbt debe estar dentro del contenedor o en el entorno local; no debe asumirse que está globalmente instalado en el host.

## Pipeline & Integration

- La coordinación entre la sincronización de Airbyte, la carga en MinIO y el disparo de los modelos dbt requiere una buena orquestación y manejo de estados.
- Usar tareas en Airflow para obtener tokens, lanzar sincronizaciones y monitorear estado simplifica la automatización.
- Los tiempos de espera y reintentos son importantes para evitar colisiones o duplicidades en los datos.

## Docker & DevOps

- Usar comandos de Docker Compose específicos para levantar, parar o reiniciar servicios individuales agiliza el desarrollo.
- `docker compose up -d --no-deps --build <service>` permite aplicar cambios sin bajar toda la infraestructura.
- Limpiar recursos no usados con `docker system prune` evita consumo innecesario de espacio.
- Un `Makefile` con comandos frecuentes puede ahorrar tiempo y reducir errores al tipear.

---


Lessons Learned: Full Stack Data Pipeline Setup
1. dbt + Airflow (Astro) Integration

Profiles placement matters:
profiles.yml must be in a directory referenced by DBT_PROFILES_DIR (e.g. /usr/local/airflow/dags/dbt/maritime_dw) for dbt commands to run properly inside containers.

Correct .env usage:
.env must define all required env vars. Airflow reads from this during container startup, so changes may require astro dev restart.

Volume mounts in containers:
When running astro dev, your local files (like dbt models and profiles.yml) get mounted into the container. Keep your dbt project self-contained inside astro/dags/dbt/... to avoid confusion.

2. Working with Docker Containers

Permissions matter:
dbt failed initially due to permission issues writing to logs/dbt.log.
🔧 Solution: Run chmod -R 777 dbt in the container (or set correct ownership).

Environment consistency:
You used docker exec -it to troubleshoot inside the container. Always test dbt builds from within the same environment Airflow runs them (i.e. the scheduler container).

3. Dynamic IPs and Hostnames

Use container names over IPs:
Replace hardcoded IPs (like 192.168.x.x) with Docker service names, e.g.:

MINIO_ENDPOINT=minio:9000
POSTGRES_DESTINATION_HOST=postgres-destination


This avoids issues when IPs change between reboots or networks.

4. Airbyte and dbt Automation in DAGs

Airbyte OAuth token required:
You built a helper to retrieve the token from Airbyte before triggering syncs. This makes your DAG more robust.

dbt via subprocess.run() works but...
You're currently calling dbt build using Python's subprocess. While functional, this can be improved with Cosmos' DbtTaskGroup for better task separation and observability.

5. Debugging Best Practices

Use dbt debug inside the container to test connectivity and validate config.

Test dbt list to ensure your models and project load correctly.

Read Airflow logs carefully, especially for stderr and paths (like missing dbt_project.yml).

Validate ETL success via queries like:

SELECT MAX(_airbyte_extracted_at) FROM public.gold;

6. Versioning & Git Workflow

Commit all relevant dbt project files, including:

dbt_project.yml

profiles.yml (unless excluded)

models/, seeds/, snapshots/, macros/

Clean up .gitignore to avoid accidentally excluding important pieces.

¡Estos apuntes ayudarán a que el proyecto sea más mantenible y escalable a futuro!