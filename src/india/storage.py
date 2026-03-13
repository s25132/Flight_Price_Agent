import os
import boto3


def upload_model(train_result):

    run_id = train_result["run_id"]
    model_dir = train_result["model_dir"]

    endpoint = os.environ["MINIO_ENDPOINT"]
    bucket = os.environ["MINIO_BUCKET"]

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=os.environ["MINIO_ACCESS_KEY"],
        aws_secret_access_key=os.environ["MINIO_SECRET_KEY"],
    )

    latest_prefix = f"india_models/latest/"

    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=latest_prefix):
        for obj in page.get("Contents", []):
            s3.delete_object(Bucket=bucket, Key=obj["Key"])

    for root, _, files in os.walk(model_dir):

        for f in files:

            local_file = os.path.join(root,f)

            # archiwum runów
            run_key = f"india_models/run/{run_id}/" + os.path.relpath(local_file, model_dir)

            # aktualny model
            latest_key = latest_prefix + os.path.relpath(local_file, model_dir)

            s3.upload_file(local_file, bucket, run_key)
            s3.upload_file(local_file, bucket, latest_key)

            print(f"Uploaded {local_file} -> {run_key}")
            print(f"Updated latest -> {latest_key}")