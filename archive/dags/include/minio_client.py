import os
from dotenv import load_dotenv
from minio import Minio

# load vars from .env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


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
