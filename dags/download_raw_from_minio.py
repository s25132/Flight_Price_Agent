from __future__ import annotations

from fileinput import filename
import os
from datetime import datetime

import boto3
from airflow import DAG
from airflow.operators.python import PythonOperator


def download_raw_from_minio() -> None:
    endpoint = os.environ["MINIO_ENDPOINT"]
    access_key = os.environ["MINIO_ACCESS_KEY"]
    secret_key = os.environ["MINIO_SECRET_KEY"]
    bucket = os.environ["MINIO_BUCKET"]

    prefix = "raw/"
    local_base_dir = "/opt/airflow/data/raw"
    os.makedirs(local_base_dir, exist_ok=True)

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )

    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    contents = response.get("Contents", [])

    downloaded = 0
    for obj in contents:
        key = obj["Key"]

        if key.endswith("/"):
            continue

        relative_path = key[len(prefix):]
        local_path = os.path.join(local_base_dir, relative_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        s3.download_file(bucket, key, local_path)
        print(f"Downloaded {key} -> {local_path}")
        downloaded += 1

    print(f"Downloaded files: {downloaded}")


with DAG(
    dag_id="download_raw_from_minio",
    schedule=None,
    catchup=False,
    tags=["minio", "raw"],
) as dag:
    PythonOperator(
        task_id="download_raw_from_minio",
        python_callable=download_raw_from_minio,
    )