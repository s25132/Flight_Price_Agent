from datetime import datetime
from airflow.decorators import dag, task

from src.india.data_io import download_data
from src.india.preprocessing import preprocess 
from src.india.training import train_model 
from src.india.evaluation import evaluate_model
from src.india.storage import upload_model
from src.india.split_data import split_data


@dag(
    dag_id="training_pipeline_india",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["ml", "minio", "model", "training", "india"],
    params={
        "experiment_name": "india_autogluon_training",
        "target": "price"
    }
)
def training_pipeline():

    @task
    def get_params(**context):
        return {
            "experiment_name": context["params"]["experiment_name"],
            "target": context["params"]["target"],
        }

    @task
    def download():
        return download_data()

    @task
    def preprocess_task(path):
        return preprocess(path)
    
    @task(multiple_outputs=True)
    def split_task(path):
        return split_data(path)

    @task
    def train_task(path, config):
        return train_model(
            path=path,
            experiment_name=config["experiment_name"],
            target=config["target"],
        )

    @task
    def evaluate_task(path, train_result, config):
        return evaluate_model(path, train_result, experiment_name=config["experiment_name"], target=config["target"])

    @task
    def upload_task(train_result):
        upload_model(train_result)

    config = get_params()

    raw = download()
    processed = preprocess_task(raw)
    split_result = split_task(processed)

    train_result = train_task(split_result["train_path"], config)
    evaluation_result = evaluate_task(split_result["test_path"], train_result, config)
    upload = upload_task(train_result)

    config >> raw >> processed >> split_result >> train_result >> [evaluation_result, upload]

dag = training_pipeline()