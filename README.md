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


# 🌊 Modern Maritime Data Stack

Este proyecto crea un pipeline analítico simulando tráfico marítimo, utilizando herramientas modernas como Airflow, DBT, MinIO y Superset.

---

## 📁 Estructura del proyecto

modern-maritime-data-stack/
│
├── data_collector/ # Scripts para consumir datos (API o fake)
│ └── main.py
├── astro/ # Proyecto Airflow
├── dbt/ # Proyecto DBT
├── superset/ # Configuración de dashboards
├── setup.sh # Script para configurar entorno local
├── requirements.txt # Librerías necesarias
├── .env # Variables de entorno (NO subir al repo)
├── .gitignore
└── README.md


---

## ⚙️ Requisitos

- Python 3.8 o superior
- Git
- macOS, Linux, o Windows (con WSL o Git Bash)

---

## 🚀 Instalación (1 minuto)

1. Clona el repositorio:

```bash
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

🛠️ Uso

Desde la root del proyecto, activa el entorno y ejecuta el colector:

source venv/bin/activate
python data_collector/main.py

Próximamente: DAGs en Airflow, transformaciones con DBT, dashboards en Superset.
🧾 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo LICENSE.

✍️ Autor

Tu nombre — @nico-de-vietri
