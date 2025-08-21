from datetime import datetime, timezone
import io
import uuid


def upload_json(client, bucket, object_name, data_bytes):
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    data_stream = io.BytesIO(data_bytes)
    client.put_object(
        bucket,
        object_name,
        data_stream,
        length=len(data_bytes),
        content_type="application/json",
    )


def generate_object_name(prefix="position_report"):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    uid = uuid.uuid4().hex[:6]  # 6-char unique suffix, added
    return f"{prefix}_{timestamp}_{uid}.json"


import os
from dotenv import load_dotenv
from minio import Minio

# load vars from .env
load_dotenv()


def get_minio_client():
    client = Minio(
        os.getenv("MINIO_ENDPOINT"),
        access_key=os.getenv("MINIO_ACCESS_KEY"),
        secret_key=os.getenv("MINIO_SECRET_KEY"),
        secure=os.getenv("MINIO_SECURE").lower() == "true",
    )
    return client


def ensure_bucket(client, bucket_name):
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' created.")
    else:
        print(f"Bucket '{bucket_name}' already exists.")
