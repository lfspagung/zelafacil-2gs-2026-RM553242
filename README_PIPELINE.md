# Pipeline de Big Data — ZelaFácil / CitizenTech

Pipeline de engenharia de dados estruturado na **Arquitetura Medallion (Bronze, Silver e Gold)**, orquestrado via **Apache Airflow**, para ingestão, tratamento, enriquecimento geográfico, anonimização em conformidade com a **LGPD** e modelagem dimensional (**Star Schema**) de chamados de zeladoria urbana e acessibilidade (ODS 10 e 11).

## Arquitetura e Fluxo da DAG

- **DAG ID:** `zelafacil_citizentech_pipeline`
- **Agendamento:** `@daily`
- **Orquestração:** `ingestao_bronze` -> `transformacao_enriquecimento_silver` -> `modelagem_star_schema_gold` -> `validacao_qualidade_dados`

| Camada | Artefato Principal | Transformações e Regras |
| --- | --- | --- |
| **Bronze (Raw)** | `pipeline/data/bronze/raw_chamados.json` | Ingestão bruta de chamados (OCR de faturas e Portal Web). |
| **Silver (Trusted)** | `pipeline/data/silver/silver_chamados.csv` | Deduplicação por protocolo (`7 -> 6`), enriquecimento de endereço via **API ViaCEP** e pseudonimização LGPD (`cidadao_hash_lgpd` em SHA-256 / `ANONIMO`). |
| **Gold (DW Star Schema)** | `pipeline/data/gold/zelafacil_dw.db` | Modelagem em Data Warehouse SQLite (`dim_localidade`, `dim_categoria_nbr9050`, `fato_chamados_zeladoria` e visão `gold_kpis_bairro`) vinculada às normas ABNT NBR 9050, NBR 16537 e NBR 5101. |
| **Data Quality** | `pipeline/data/gold/dq_report.json` | Validação automatizada de integridade referencial, ausência de duplicidades e conformidade LGPD (`status: PASSED`). |

## Estrutura do Pipeline

```text
pipeline/
├── dags/
│   └── zelafacil_pipeline_dag.py   # Definição da DAG no Apache Airflow
├── data/
│   ├── bronze/                     # Dados brutos (JSON)
│   ├── silver/                     # Dados tratados e enriquecidos (CSV)
│   └── gold/                       # Star Schema (CSV, SQLite DW e dq_report.json)
└── etl_zelafacil.py                # Regras de ETL Medallion e Data Quality
```

## Como Executar Localmente

### 1. Ambiente Virtual e Dependências
```bash
python3 -m venv .venv_pipeline
source .venv_pipeline/bin/activate
pip install pandas requests
```

### 2. Execução Direta do Pipeline ETL
```bash
python pipeline/etl_zelafacil.py
```

### 3. Validação do Data Warehouse SQLite e Data Quality
```bash
python -c "
import sqlite3, json, pandas as pd
with sqlite3.connect('pipeline/data/gold/zelafacil_dw.db') as conn:
    for t in ['dim_localidade', 'dim_categoria_nbr9050', 'fato_chamados_zeladoria', 'gold_kpis_bairro']:
        print(f'\n=== {t} ===')
        print(pd.read_sql(f'SELECT * FROM {t}', conn).to_string(index=False))
print('\n=== dq_report.json ===')
print(json.dumps(json.loads(open('pipeline/data/gold/dq_report.json').read()), indent=2, ensure_ascii=False))
"
```

### 4. Orquestração com Apache Airflow (Python 3.9 / macOS)
```bash
AIRFLOW_VERSION=2.10.5
CONSTRAINT_URL="[https://raw.githubusercontent.com/apache/airflow/constraints-$](https://raw.githubusercontent.com/apache/airflow/constraints-$){AIRFLOW_VERSION}/constraints-3.9.txt"
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"

export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export NO_PROXY="*"
export AIRFLOW_HOME=~/airflow_zelafacil
export AIRFLOW__CORE__DAGS_FOLDER="$(pwd)/pipeline/dags"
export AIRFLOW__CORE__LOAD_EXAMPLES=False

airflow db migrate
airflow dags test zelafacil_citizentech_pipeline 2026-11-19
airflow webserver --debug -H 127.0.0.1 -p 8080
```
Acesse `http://127.0.0.1:8080` para visualizar o grafo e o histórico de execução da DAG.
