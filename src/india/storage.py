import os
import boto3
import shutil
import zipfile


def upload_model(train_result):

    model_dir = train_result["model_dir"]

    endpoint = os.environ["MINIO_ENDPOINT"]
    bucket = os.environ["MINIO_BUCKET"]

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=os.environ["MINIO_ACCESS_KEY"],
        aws_secret_access_key=os.environ["MINIO_SECRET_KEY"],
    )

    latest_prefix = "india/models/latest/"

    # usuwanie poprzednich modeli z MinIO
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=latest_prefix):
        for obj in page.get("Contents", []):
            s3.delete_object(Bucket=bucket, Key=obj["Key"])

    # -----------------------------
    # 1. ZIP całego katalogu modelu
    # -----------------------------
    zip_path = os.path.join(model_dir, "model.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(model_dir):
            for f in files:
                file_path = os.path.join(root, f)

                # nie pakuj samego zipa
                if file_path == zip_path:
                    continue

                arcname = os.path.relpath(file_path, model_dir)
                zipf.write(file_path, arcname)

    print(f"Model zipped -> {zip_path}")

    # -----------------------------
    # 2. Upload ZIP do MinIO
    # -----------------------------
    latest_key = latest_prefix + "model.zip"

    s3.upload_file(zip_path, bucket, latest_key)

    print(f"Uploaded zipped model -> {latest_key}")

    # -----------------------------
    # 3. Usunięcie zawartości model_dir
    # -----------------------------
    for item in os.listdir(model_dir):
        item_path = os.path.join(model_dir, item)

        if os.path.isfile(item_path):
            os.remove(item_path)
        else:
            shutil.rmtree(item_path)

    print(f"Cleaned local directory -> {model_dir}")