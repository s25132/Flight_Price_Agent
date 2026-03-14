import os
import mlflow
import pandas as pd
from autogluon.tabular import TabularPredictor


def train_model(path, experiment_name, target):
    df = pd.read_csv(path)

    model_dir = "/opt/airflow/data/models/india/autogluon"

    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    mlflow.set_experiment(experiment_name)

    label=target
    problem_type="regression"
    eval_metric="root_mean_squared_error"
    presets="medium_quality"
    time_limit=600
    train_data=df

    with mlflow.start_run() as run:
        predictor = TabularPredictor(
            label=label,
            path=model_dir,
            problem_type=problem_type,
            eval_metric=eval_metric,
        ).fit(
            train_data=train_data,
            presets=presets,
            time_limit=time_limit,
        )

        mlflow.log_param("problem_type", problem_type)
        mlflow.log_param("eval_metric", eval_metric)
        mlflow.log_param("presets", presets)
        mlflow.log_param("time_limit", time_limit)
        mlflow.log_param("target", label)

        return {
            "run_id": run.info.run_id,
            "model_dir": model_dir,
        }