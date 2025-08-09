FROM python:3.11-slim

# Install dependencies including git
RUN apt-get update && apt-get install -y build-essential libpq-dev git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies including dbt-code and dbt-postgres
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the project files
COPY . .

# Default shell
ENTRYPOINT ["bash"]



