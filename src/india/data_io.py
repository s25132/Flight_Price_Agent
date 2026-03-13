import os
import boto3


def download_data():

    endpoint = os.environ["MINIO_ENDPOINT"]
    bucket = os.environ["MINIO_BUCKET"]

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=os.environ["MINIO_ACCESS_KEY"],
        aws_secret_access_key=os.environ["MINIO_SECRET_KEY"],
    )

    key = "raw/india.csv"
    local_path = "/opt/airflow/data/raw/india.csv"

    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    s3.download_file(bucket, key, local_path)

    return local_path