from datetime import datetime

import boto3
import os

from airflow import DAG
from airflow.operators.python import PythonOperator


def promote_latest_model_to_best():
    endpoint = os.environ["MINIO_ENDPOINT"]
    bucket = os.environ["MINIO_BUCKET"]

    source_key = "india/models/latest/model.zip"
    destination_key = "india/models/best/model.zip"

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=os.environ["MINIO_ACCESS_KEY"],
        aws_secret_access_key=os.environ["MINIO_SECRET_KEY"],
    )

    copy_source = {
        "Bucket": bucket,
        "Key": source_key,
    }

    s3.copy_object(
        Bucket=bucket,
        CopySource=copy_source,
        Key=destination_key,
    )

    print(f"Copied model from {source_key} to {destination_key}")


with DAG(
    dag_id="promote_latest_india_model_to_best",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["ml", "minio", "model", "promotion", "india"],
) as dag:

    promote_model = PythonOperator(
        task_id="promote_latest_india_model_to_best",
        python_callable=promote_latest_model_to_best,
    )

    promote_model