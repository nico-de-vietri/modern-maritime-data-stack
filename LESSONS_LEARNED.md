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

¡Estos apuntes ayudarán a que el proyecto sea más mantenible y escalable a futuro!