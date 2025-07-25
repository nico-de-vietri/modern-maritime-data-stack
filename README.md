# modern-maritime-data-stack
# Data Engineering Project Rolling Code School

#  Modern Maritime Data Stack

Proyecto final de análisis de tráfico marítimo en tiempo real usando el Modern Data Stack.

##  Stack utilizado

- Fuente de datos: [AISStream.io](https://aisstream.io)
- Almacenamiento raw: MinIO (S3 local)
- Orquestación: Apache Airflow
- Transformación: dbt
- Visualización: Superset (o alternativa)

##  Estructura del proyecto

- `data_collector/`: Script para capturar datos de AISStream y guardarlos en MinIO
- `airflow/`: DAGs y configuración de pipelines
- `dbt_project/`: Transformaciones y modelo analítico
- `minio/`: Almacenamiento tipo S3
- `superset/`: Configuración de dashboards

##  Cómo ejecutar

Se usará `docker-compose` para levantar todos los servicios.

Próximamente más instrucciones...
