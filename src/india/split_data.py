import os
import pandas as pd
from sklearn.model_selection import train_test_split


def split_data(path):
    df = pd.read_csv(path)

    train_df, test_df = train_test_split(
        df,
        test_size=0.2,
        random_state=42
    )

    train_path = "/opt/airflow/data/processed/india/train_split.csv"
    test_path = "/opt/airflow/data/processed/india/test_split.csv"

    os.makedirs(os.path.dirname(train_path), exist_ok=True)

    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    return {
        "train_path": train_path,
        "test_path": test_path
    }