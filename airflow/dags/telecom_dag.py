
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import shutil
import subprocess


from datetime import datetime
import os
import shutil
import subprocess

#  BASE PATH
BASE_PATH = "/home/srirangasuthant/telecom-intelligence"

LANDING_PATH = f"{BASE_PATH}/data/landing/"
RAW_PATH = f"{BASE_PATH}/data/raw/"
REJECTED_PATH = f"{BASE_PATH}/data/rejected/"


#  1. Detect files
def detect_files(**kwargs):
    files = os.listdir(LANDING_PATH)
    csv_files = [f for f in files if f.endswith(".csv")]

    if not csv_files:
        raise ValueError(" No CSV files found in landing!")

    print(" Detected files:", csv_files)
    return csv_files


#  2. Validate files
def validate_files(**kwargs):
    files = kwargs['ti'].xcom_pull(task_ids='detect_files')

    valid_files = []
    invalid_files = []

    for f in files:
        file_path = os.path.join(LANDING_PATH, f)

        if os.path.getsize(file_path) > 0:
            valid_files.append(f)
        else:
            invalid_files.append(f)

    print(" Valid files:", valid_files)
    print(" Invalid files:", invalid_files)

    return {"valid": valid_files, "invalid": invalid_files}


#  3. Move files
def move_files(**kwargs):
    data = kwargs['ti'].xcom_pull(task_ids='validate_files')

    valid_files = data["valid"]
    invalid_files = data["invalid"]

    for f in valid_files:
        shutil.move(
            os.path.join(LANDING_PATH, f),
            os.path.join(RAW_PATH, f)
        )

    for f in invalid_files:
        shutil.move(
            os.path.join(LANDING_PATH, f),
            os.path.join(REJECTED_PATH, f)
        )

    print(" Files moved successfully")


#  4. Log status
def log_status(**kwargs):
    print(" File processing completed")


#  5. Run Spark job
def run_spark_job(**kwargs):
    print(" Running Spark pipeline...")

    subprocess.run(
        [   
            "/home/srirangasuthant/telecom-intelligence/venv/bin/python",
            f"{BASE_PATH}/spark/telecom_pipeline.py"
        ],
        cwd=BASE_PATH,
        check=True
    )

    print(" Spark job completed")


#  6. Notify
def notify(**kwargs):
    print("Pipeline completed successfully")


#  DAG
with DAG(
    dag_id="telecom_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False
) as dag:

    detect = PythonOperator(
        task_id="detect_files",
        python_callable=detect_files
    )

    validate = PythonOperator(
        task_id="validate_files",
        python_callable=validate_files
    )

    move = PythonOperator(
        task_id="move_files",
        python_callable=move_files
    )

    log = PythonOperator(
        task_id="log_status",
        python_callable=log_status
    )

    spark = PythonOperator(
        task_id="run_spark_job",
        python_callable=run_spark_job
    )

    notify_task = PythonOperator(
        task_id="notify",
        python_callable=notify
    )

    #  FLOW
    detect >> validate >> move >> log >> spark >> notify_task