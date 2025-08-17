import os
import json
import asyncio
import time
from dotenv import load_dotenv

from include.minio_client import get_minio_client, ensure_bucket
from include.ais_websocket import listen_and_process
from include.minio_utils import generate_object_name, upload_json

# Cargamos variables de entorno desde el .env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

BUCKET_NAME = os.getenv("MINIO_BUCKET")


class BatchUploader:
    def __init__(self, minio_client, bucket, batch_size=100, max_wait=10):
        self.minio_client = minio_client
        self.bucket = bucket
        self.batch_size = batch_size
        self.max_wait = max_wait
        self.batch = []
        self.last_upload_time = time.time()

    async def add_and_upload(self, position_data):
        self.batch.append(position_data)
        now = time.time()
        if (
            len(self.batch) >= self.batch_size
            or (now - self.last_upload_time) > self.max_wait
        ):
            await self.upload_batch()
            self.last_upload_time = now

    async def upload_batch(self):
        if not self.batch:
            return
        filename = generate_object_name()

        # data_bytes = json.dumps(self.batch).encode("utf-8")
        # converting array to json lines
        data_bytes = "\n".join(json.dumps(item) for item in self.batch).encode("utf-8")
        upload_json(self.minio_client, self.bucket, filename, data_bytes)
        # print(f"Uploaded batch {filename} with {len(self.batch)} records")
        print(f"Uploaded batch {filename} with {len(self.batch)} records (JSON Lines)")
        self.batch.clear()


async def process_and_upload_factory():
    # this function creates an instance of minio and batch uploader,
    # returns a function that will be used to process each position.
    minio_client = get_minio_client()
    ensure_bucket(minio_client, BUCKET_NAME)
    batch_uploader = BatchUploader(minio_client, BUCKET_NAME)

    async def process_and_upload(position_data):
        await batch_uploader.add_and_upload(position_data)

    return process_and_upload


def run_ingestion():
    # Creates a processing at runtime function
    process_and_upload = asyncio.run(process_and_upload_factory())
    # Exec listen_and_process , listen seconds can vary
    asyncio.run(listen_and_process(process_and_upload, listen_seconds=300))


if __name__ == "__main__":
    process_and_upload = asyncio.run(process_and_upload_factory())
    asyncio.run(listen_and_process(process_and_upload))


# import os
# import json
# import asyncio
# import time
# from dotenv import load_dotenv

# from include.minio_client import get_minio_client, ensure_bucket
# from include.ais_websocket import listen_and_process
# from include.minio_utils import generate_object_name, upload_json

# # Cargamos variables de entorno desde el .env
# load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# BUCKET_NAME = os.getenv("MINIO_BUCKET")
# minio_client = get_minio_client()
# ensure_bucket(minio_client, BUCKET_NAME)


# # Batching
# class BatchUploader:
#     def __init__(self, minio_client, bucket, batch_size=100, max_wait=10):
#         self.minio_client = minio_client
#         self.bucket = bucket
#         self.batch_size = batch_size
#         self.max_wait = max_wait
#         self.batch = []
#         self.last_upload_time = time.time()

#     async def add_and_upload(self, position_data):
#         self.batch.append(position_data)
#         now = time.time()
#         if (
#             len(self.batch) >= self.batch_size
#             or (now - self.last_upload_time) > self.max_wait
#         ):
#             await self.upload_batch()
#             self.last_upload_time = now

#     async def upload_batch(self):
#         if not self.batch:
#             return
#         filename = generate_object_name()
#         data_bytes = json.dumps(self.batch).encode("utf-8")
#         upload_json(self.minio_client, self.bucket, filename, data_bytes)
#         print(f"Uploaded batch {filename} with {len(self.batch)} records")
#         self.batch.clear()


# # Instancia global (como antes)
# batch_uploader = BatchUploader(minio_client, BUCKET_NAME)


# # Esta función es la que escucha el websocket
# async def process_and_upload(position_data):
#     await batch_uploader.add_and_upload(position_data)


# def run_ingestion():
#     # Escuchá 30 segundos por ejecución
#     asyncio.run(listen_and_process(process_and_upload, listen_seconds=30))


# if __name__ == "__main__":
#     asyncio.run(listen_and_process(process_and_upload))
