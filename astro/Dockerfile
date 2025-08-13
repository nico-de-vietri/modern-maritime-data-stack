FROM astrocrpublic.azurecr.io/astronomer/astro-runtime:13.1.0

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install OS packages needed for dbt-postgres
USER root
RUN apt-get update && apt-get install -y libpq-dev python-dev-is-python3 gcc

# Install dbt in its own virtual environment
# RUN python -m venv /usr/local/airflow/dbt_venv && \
#     /usr/local/airflow/dbt_venv/bin/pip install --no-cache-dir dbt-postgres astronomer-cosmos && \
#     ln -s /usr/local/airflow/dbt_venv/bin/dbt /usr/local/bin/dbt    
RUN python3 -m venv /usr/local/airflow/dbt_venv && \
    /usr/local/airflow/dbt_venv/bin/pip install --no-cache-dir dbt-postgres astronomer-cosmos && \
    ln -sf /usr/local/airflow/dbt_venv/bin/dbt /usr/local/bin/dbt

USER root
RUN apt-get update && apt-get install -y git
USER astro


# FROM astrocrpublic.azurecr.io/astronomer/astro-runtime:13.1.0

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

