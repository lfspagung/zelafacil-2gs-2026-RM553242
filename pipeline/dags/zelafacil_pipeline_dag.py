import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator

# Garante que a pasta pipeline/ esteja no PYTHONPATH
PIPELINE_DIR = Path(__file__).resolve().parents[1]
if str(PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(PIPELINE_DIR))

from etl_zelafacil import (
    extract_bronze,
    model_gold,
    transform_silver,
    validate_data_quality,
)

default_args = {
    "owner": "zelafacil_rm553242",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="zelafacil_citizentech_pipeline",
    description="Pipeline Medallion (Bronze -> Silver -> Gold) do MVP ZelaFácil (ODS 10 e 11)",
    default_args=default_args,
    start_date=datetime(2026, 11, 1),
    schedule="@daily",
    catchup=False,
    tags=["fiap", "gs2026", "citizentech", "zelafacil", "medallion"],
) as dag:
    t1_ingestao_bronze = PythonOperator(
        task_id="ingestao_bronze",
        python_callable=extract_bronze,
    )

    t2_transformacao_silver = PythonOperator(
        task_id="transformacao_enriquecimento_silver",
        python_callable=transform_silver,
    )

    t3_modelagem_gold = PythonOperator(
        task_id="modelagem_star_schema_gold",
        python_callable=model_gold,
    )

    t4_validacao_dq = PythonOperator(
        task_id="validacao_qualidade_dados",
        python_callable=validate_data_quality,
    )

    t1_ingestao_bronze >> t2_transformacao_silver >> t3_modelagem_gold >> t4_validacao_dq
