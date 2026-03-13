import pandas as pd
import os


def preprocess(path):

    df = pd.read_csv(path)

    df = df.dropna()

    out_path = "/opt/airflow/data/processed/train_processed.csv"

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    df.to_csv(out_path, index=False)

    return out_path