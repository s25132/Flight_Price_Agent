import json
import os

import mlflow
import pandas as pd
from autogluon.tabular import TabularPredictor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def evaluate_model(path, train_result, experiment_name, target):
    run_id = train_result["run_id"]
    model_dir = train_result["model_dir"]

    df = pd.read_csv(path)

    predictor = TabularPredictor.load(model_dir)

    y_true = df[target]
    X = df.drop(columns=[target])

    y_pred = predictor.predict(X)

    baseline = y_true.mean()
    baseline_mae = abs(y_true - baseline).mean()
    model_mae = mean_absolute_error(y_true, y_pred)
    improvement = (baseline_mae - model_mae) / baseline_mae * 100

    metrics = {
        "mae": float(model_mae),
        "mae_percent": float(model_mae / y_true.mean() * 100),
        "baseline_mae": float(baseline_mae),
        "improvement": float(improvement),
        "rmse": float(mean_squared_error(y_true, y_pred) ** 0.5),
        "r2": float(r2_score(y_true, y_pred)),
    }

    report_dir = "/opt/airflow/data/india/reports"
    os.makedirs(report_dir, exist_ok=True)

    metrics_path = os.path.join(report_dir, "metrics.json")

    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)


    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run(run_id=run_id):
        mlflow.log_metrics(metrics)
        mlflow.log_artifact(metrics_path)

    for file in os.listdir(report_dir):
        file_path = os.path.join(report_dir, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    print(f"Cleaned report directory -> {report_dir}")
    

    return {
        "run_id": run_id,
        "metrics": metrics,
        "metrics_path": metrics_path,
    }