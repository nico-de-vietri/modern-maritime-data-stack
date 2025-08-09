FROM python:3.11-slim

# Install tools and DuckDB CLI
RUN apt-get update && apt-get install -y wget unzip && \
    wget -O duckdb_cli.zip https://github.com/duckdb/duckdb/releases/download/v0.10.1/duckdb_cli-linux-amd64.zip && \
    unzip duckdb_cli.zip && \
    mv duckdb /usr/local/bin/duckdb && \
    chmod +x /usr/local/bin/duckdb && \
    rm duckdb_cli.zip && \
    apt-get remove --purge -y wget unzip && \
    apt-get autoremove -y && \
    apt-get clean

# Verify DuckDB CLI is available
RUN duckdb --version

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the project files
COPY . .

# Default shell
ENTRYPOINT ["bash"]



