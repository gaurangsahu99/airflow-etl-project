from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models import Variable
from datetime import datetime, timedelta
import requests
import json

CITY = "Delhi"

RAW_FILE = "/tmp/raw.json"
TRANSFORMED_FILE = "/tmp/transformed.json"


def extract():
    api_key = Variable.get("API_KEY")

    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={api_key}&units=metric"

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"API failed: {response.text}")

    data = response.json()

    with open(RAW_FILE, "w") as f:
        json.dump(data, f)

    return RAW_FILE


def transform(**context):
    file_path = context['ti'].xcom_pull(task_ids="extract")

    with open(file_path) as f:
        data = json.load(f)

    transformed_data = {
        "city": data.get("name"),
        "temperature": data.get("main", {}).get("temp"),
        "humidity": data.get("main", {}).get("humidity"),
        "weather": data.get("weather", [{}])[0].get("description"),
        "timestamp": data.get("dt")
    }

    with open(TRANSFORMED_FILE, "w") as f:
        json.dump(transformed_data, f)

    return TRANSFORMED_FILE


def load_s3(**context):
    s3 = S3Hook(aws_conn_id="aws_default")

    bucket = Variable.get("S3_BUCKET")

    file_path = context['ti'].xcom_pull(task_ids="transform")

    s3.load_file(
        filename=file_path,
        key=f"processed/weather/{context['ds']}/data.json",
        bucket_name=bucket,
        replace=True
    )


def load_postgres(**context):
    pg = PostgresHook(postgres_conn_id="postgres_default")

    file_path = context['ti'].xcom_pull(task_ids="transform")

    with open(file_path) as f:
        data = json.load(f)

    timestamp = datetime.fromtimestamp(data["timestamp"])

    query = """
    INSERT INTO weather_data (city, temperature, humidity, weather, timestamp)
    VALUES (%s, %s, %s, %s, %s)
    """

    pg.run(query, parameters=(
        data["city"],
        data["temperature"],
        data["humidity"],
        data["weather"],
        timestamp
    ))


default_args = {
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="etl_weather_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args=default_args
) as dag:

    t1 = PythonOperator(task_id="extract", python_callable=extract)
    t2 = PythonOperator(task_id="transform", python_callable=transform)
    t3 = PythonOperator(task_id="load_s3", python_callable=load_s3)
    t4 = PythonOperator(task_id="load_postgres", python_callable=load_postgres)

    t1 >> t2 >> [t3, t4]