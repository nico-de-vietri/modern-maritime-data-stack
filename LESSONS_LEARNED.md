# Lessons Learned

## Project Setup and Architecture

- Decidí separar Airbyte, Airflow (Astro CLI) y los servicios de infraestructura (MinIO, Postgres, dbt) en bloques separados para mantener cada componente independiente y facilitar debugging.
- Montar volúmenes en Docker Compose para los proyectos de dbt facilita el desarrollo local y evitar rebuilds constantes.
- Usar `docker exec` para entrar en contenedores individuales y probar comandos agiliza el desarrollo.
- Variables sensibles se manejan mejor con archivos `.env` para no hardcodearlas en configuraciones ni código.

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