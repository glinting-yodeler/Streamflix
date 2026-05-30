from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

DEFAULT_ARGS = {
    "owner": "streamflix",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="streamflix_daily_pipeline",
    description="STARZPLAY-inspired OTT ETL, ML, recommendation, and summary pipeline",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["data-engineering", "ott", "streaming", "ml"],
) as dag:

    seed_dimensions = BashOperator(
        task_id="seed_dimensions",
        bash_command="cd /opt/airflow/project && python -m src.seed_dimensions",
    )

    clean_events = BashOperator(
        task_id="clean_events",
        bash_command="cd /opt/airflow/project && python -m src.clean_events",
    )

    build_marts = BashOperator(
        task_id="build_marts",
        bash_command="cd /opt/airflow/project && python -m src.build_marts",
    )

    train_churn = BashOperator(
        task_id="train_churn_model",
        bash_command="cd /opt/airflow/project && python -m src.train_churn",
    )

    generate_recommendations = BashOperator(
        task_id="generate_recommendations",
        bash_command="cd /opt/airflow/project && python -m src.recommend",
    )

    generate_summary = BashOperator(
        task_id="generate_executive_summary",
        bash_command="cd /opt/airflow/project && python -m src.genai_summary",
    )

    seed_dimensions >> clean_events >> build_marts >> train_churn >> generate_recommendations >> generate_summary
