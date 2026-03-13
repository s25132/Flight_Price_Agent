import os
import mlflow
import pandas as pd
from autogluon.tabular import TabularPredictor


def train_model(path):
    df = pd.read_csv(path)

    label = "price"
    model_dir = "/opt/airflow/data/models/autogluon"

    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    mlflow.set_experiment("autogluon-regression-india")

    with mlflow.start_run() as run:
        predictor = TabularPredictor(
            label=label,
            path=model_dir,
            problem_type="regression",
            eval_metric="root_mean_squared_error",
        ).fit(
            train_data=df,
            presets="medium_quality",
            time_limit=600,
        )

        mlflow.log_param("problem_type", "regression")
        mlflow.log_param("eval_metric", "root_mean_squared_error")
        mlflow.log_param("presets", "medium_quality")

        return {
            "run_id": run.info.run_id,
            "model_dir": model_dir,
        }