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
