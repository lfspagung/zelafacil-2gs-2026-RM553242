import hashlib
import json
import logging
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("zelafacil_etl")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"

for folder in (BRONZE_DIR, SILVER_DIR, GOLD_DIR):
    folder.mkdir(parents=True, exist_ok=True)


def _hash_pii(valor: str) -> str:
    """Anonimiza dados pessoais (LGPD) usando SHA-256 truncado."""
    if not valor or pd.isna(valor):
        return "ANONIMO"
    return hashlib.sha256(str(valor).strip().encode("utf-8")).hexdigest()[:16]


def _normalizar_cep(cep: str) -> str:
    digitos = re.sub(r"\D", "", str(cep or ""))
    if len(digitos) == 8:
        return f"{digitos[:5]}-{digitos[5:]}"
    return "00000-000"


def _consultar_viacep(cep_formatado: str, cache: dict) -> dict:
    """Consulta a API pública ViaCEP com cache em memória e fallback seguro."""
    if cep_formatado in cache:
        return cache[cep_formatado]

    digitos = cep_formatado.replace("-", "")
    fallback = {
        "logradouro": "Não informado",
        "bairro": "Não informado",
        "cidade": "São Paulo",
        "uf": "SP",
    }

    if len(digitos) != 8 or digitos == "00000000":
        cache[cep_formatado] = fallback
        return fallback

    try:
        resp = requests.get(f"https://viacep.com.br/ws/{digitos}/json/", timeout=5)
        if resp.status_code == 200:
            payload = resp.json()
            if not payload.get("erro"):
                resultado = {
                    "logradouro": payload.get("logradouro") or "Não informado",
                    "bairro": payload.get("bairro") or "Centro",
                    "cidade": payload.get("localidade") or "São Paulo",
                    "uf": payload.get("uf") or "SP",
                }
                cache[cep_formatado] = resultado
                return resultado
    except requests.RequestException as exc:
        logger.warning("Falha na consulta ViaCEP para %s: %s", cep_formatado, exc)

    cache[cep_formatado] = fallback
    return fallback


# ==============================================================================
# TAREFA 1 — INGESTÃO (CAMADA BRONZE)
# ==============================================================================
def extract_bronze() -> str:
    """Ingere chamados brutos (simulação justificada baseada no MVP ZelaFácil)."""
    ts_ingestao = datetime.now(timezone.utc).isoformat()

    registros_brutos = [
        {
            "protocolo": "ZF-2026-0001",
            "data_abertura": "2026-11-10 08:15:00",
            "cidadao_nome": "Jose Carlos da Silva",
            "cep_informado": "08674010",
            "categoria": "Rampa de Acessibilidade",
            "descricao": "Rampa destruída na esquina impede passagem de cadeirante.",
            "gravidade": "Alta",
            "status": "Em Análise",
            "origem_dado": "OCR_Fatura",
            "tempo_resolucao_horas": None,
        },
        {
            "protocolo": "ZF-2026-0001",  # Duplicidade proposital para tratamento na Silver
            "data_abertura": "2026-11-10 08:15:00",
            "cidadao_nome": "Jose Carlos da Silva",
            "cep_informado": "08674-010",
            "categoria": "Rampa de Acessibilidade",
            "descricao": "Rampa destruída na esquina impede passagem de cadeirante.",
            "gravidade": "Alta",
            "status": "Em Análise",
            "origem_dado": "OCR_Fatura",
            "tempo_resolucao_horas": None,
        },
        {
            "protocolo": "ZF-2026-0002",
            "data_abertura": "2026-11-11 14:30:00",
            "cidadao_nome": "Maria Oliveira",
            "cep_informado": "01310-100",
            "categoria": "Piso Tátil",
            "descricao": "Piso tátil solto próximo ao ponto de ônibus.",
            "gravidade": "Alta",
            "status": "Concluído",
            "origem_dado": "Portal_Web",
            "tempo_resolucao_horas": 48.0,
        },
        {
            "protocolo": "ZF-2026-0003",
            "data_abertura": "2026-11-12 09:45:00",
            "cidadao_nome": "Carlos Eduardo Santos",
            "cep_informado": "05508-000",
            "categoria": "Calçada Irregular",
            "descricao": "Buraco profundo na calçada em frente à UBS.",
            "gravidade": "Crítica",
            "status": "Encaminhado 156",
            "origem_dado": "OCR_Fatura",
            "tempo_resolucao_horas": 72.0,
        },
        {
            "protocolo": "ZF-2026-0004",
            "data_abertura": "2026-11-14 19:20:00",
            "cidadao_nome": "Ana Paula Ferreira",
            "cep_informado": "08674-010",
            "categoria": "Iluminação Pública",
            "descricao": "Poste apagado há 5 dias em travessia de pedestres.",
            "gravidade": "Média",
            "status": "Concluído",
            "origem_dado": "Portal_Web",
            "tempo_resolucao_horas": 24.0,
        },
        {
            "protocolo": "ZF-2026-0005",
            "data_abertura": "2026-11-16 11:05:00",
            "cidadao_nome": "Roberto Almeida",
            "cep_informado": "04101-300",
            "categoria": "Semáforo Sonoro",
            "descricao": "Sinal sonoro para deficientes visuais inoperante.",
            "gravidade": "Crítica",
            "status": "Em Análise",
            "origem_dado": "OCR_Fatura",
            "tempo_resolucao_horas": None,
        },
        {
            "protocolo": "ZF-2026-0006",
            "data_abertura": "2026-11-17 16:40:00",
            "cidadao_nome": None,  # Nulo proposital
            "cep_informado": "01310100",
            "categoria": "Calçada Irregular",
            "descricao": "Raiz de árvore levantando bloquetes da calçada.",
            "gravidade": "Média",
            "status": "Encaminhado 156",
            "origem_dado": "Portal_Web",
            "tempo_resolucao_horas": 60.0,
        },
    ]

    envelope = {
        "pipeline": "zelafacil_citizentech_etl",
        "ingested_at_utc": ts_ingestao,
        "total_registros_brutos": len(registros_brutos),
        "records": registros_brutos,
    }

    output_path = BRONZE_DIR / "raw_chamados.json"
    output_path.write_text(
        json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info("[BRONZE] %d registros salvos em %s", len(registros_brutos), output_path)
    return str(output_path)


# ==============================================================================
# TAREFA 2 — TRATAMENTO, LGPD E ENRIQUECIMENTO VIACEP (CAMADA SILVER)
# ==============================================================================
def transform_silver() -> str:
    """Limpa, deduplica, anonimiza PII (LGPD) e enriquece endereços via API ViaCEP."""
    bronze_path = BRONZE_DIR / "raw_chamados.json"
    payload = json.loads(bronze_path.read_text(encoding="utf-8"))
    df = pd.DataFrame(payload["records"])

    # 1. Deduplicação por protocolo
    antes = len(df)
    df = df.drop_duplicates(subset=["protocolo"], keep="first").copy()
    logger.info("[SILVER] Duplicidades removidas: %d -> %d", antes, len(df))

    # 2. Padronização de datas e CEP
    df["data_abertura"] = pd.to_datetime(df["data_abertura"], errors="coerce")
    df["cep"] = df["cep_informado"].apply(_normalizar_cep)

    # 3. Anonimização LGPD (remove nome em texto claro)
    df["cidadao_hash_lgpd"] = df["cidadao_nome"].apply(_hash_pii)
    df = df.drop(columns=["cidadao_nome", "cep_informado"])

    # 4. Enriquecimento geográfico real via ViaCEP
    cache_cep = {}
    geo_data = df["cep"].apply(lambda c: _consultar_viacep(c, cache_cep))
    df_geo = pd.DataFrame(geo_data.tolist(), index=df.index)
    df = pd.concat([df, df_geo], axis=1)

    # 5. Regras de negócio NBR 9050 e score de prioridade
    mapa_score = {"Baixa": 1, "Média": 2, "Alta": 3, "Crítica": 4}
    df["prioridade_score"] = df["gravidade"].map(mapa_score).fillna(2).astype(int)
    df["tempo_resolucao_horas"] = df["tempo_resolucao_horas"].fillna(0.0)
    df["processed_at_utc"] = datetime.now(timezone.utc).isoformat()

    output_path = SILVER_DIR / "silver_chamados.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")
    logger.info("[SILVER] Tabela tratada salva em %s (%d linhas)", output_path, len(df))
    return str(output_path)


# ==============================================================================
# TAREFA 3 — MODELAGEM ANALÍTICA STAR SCHEMA (CAMADA GOLD + SQLITE DW)
# ==============================================================================
def model_gold() -> str:
    """Gera tabelas dimensionais, tabela fato, KPIs agregados e carrega no SQLite DW."""
    df = pd.read_csv(SILVER_DIR / "silver_chamados.csv", encoding="utf-8")

    # Dimensão Localidade
    dim_localidade = (
        df[["cep", "logradouro", "bairro", "cidade", "uf"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    dim_localidade.insert(0, "sk_localidade", range(1, len(dim_localidade) + 1))

    # Dimensão Categoria NBR 9050
    regras_nbr = {
        "Rampa de Acessibilidade": ("ABNT NBR 9050:2020 - Item 6.12", 5),
        "Piso Tátil": ("ABNT NBR 16537 / NBR 9050", 7),
        "Calçada Irregular": ("ABNT NBR 9050:2020 - Item 6.12.3", 10),
        "Iluminação Pública": ("ABNT NBR 5101", 3),
        "Semáforo Sonoro": ("ABNT NBR 9050:2020 - Item 6.12.7", 2),
    }
    dim_categoria = (
        df[["categoria"]].drop_duplicates().reset_index(drop=True)
    )
    dim_categoria.insert(0, "sk_categoria", range(1, len(dim_categoria) + 1))
    dim_categoria["norma_tecnica"] = dim_categoria["categoria"].map(
        lambda c: regras_nbr.get(c, ("ABNT NBR 9050", 15))[0]
    )
    dim_categoria["sla_dias"] = dim_categoria["categoria"].map(
        lambda c: regras_nbr.get(c, ("ABNT NBR 9050", 15))[1]
    )

    # Tabela Fato Chamados
    fato = df.merge(dim_localidade, on=["cep", "logradouro", "bairro", "cidade", "uf"], how="left")
    fato = fato.merge(dim_categoria, on=["categoria"], how="left")
    fato_chamados = fato[
        [
            "protocolo",
            "data_abertura",
            "sk_localidade",
            "sk_categoria",
            "cidadao_hash_lgpd",
            "gravidade",
            "prioridade_score",
            "status",
            "origem_dado",
            "tempo_resolucao_horas",
            "descricao",
        ]
    ].copy()

    # Visão agregada Gold para o Painel de BI do ZelaFácil
    gold_kpis = (
        fato.groupby(["cidade", "bairro"], as_index=False)
        .agg(
            total_chamados=("protocolo", "count"),
            chamados_criticos=("prioridade_score", lambda s: int((s >= 3).sum())),
            score_medio_prioridade=("prioridade_score", "mean"),
            tempo_medio_resolucao_h=("tempo_resolucao_horas", "mean"),
        )
        .round(2)
    )

    # Salva CSVs na camada Gold
    dim_localidade.to_csv(GOLD_DIR / "dim_localidade.csv", index=False)
    dim_categoria.to_csv(GOLD_DIR / "dim_categoria_nbr9050.csv", index=False)
    fato_chamados.to_csv(GOLD_DIR / "fato_chamados_zeladoria.csv", index=False)
    gold_kpis.to_csv(GOLD_DIR / "gold_kpis_bairro.csv", index=False)

    # Carrega no Data Warehouse SQLite para consumo direto pelo MVP
    db_path = GOLD_DIR / "zelafacil_dw.db"
    with sqlite3.connect(db_path) as conn:
        dim_localidade.to_sql("dim_localidade", conn, if_exists="replace", index=False)
        dim_categoria.to_sql("dim_categoria_nbr9050", conn, if_exists="replace", index=False)
        fato_chamados.to_sql("fato_chamados_zeladoria", conn, if_exists="replace", index=False)
        gold_kpis.to_sql("gold_kpis_bairro", conn, if_exists="replace", index=False)

    logger.info("[GOLD] Star Schema e Data Warehouse salvos em %s", db_path)
    return str(db_path)


# ==============================================================================
# TAREFA 4 — VALIDAÇÃO DE QUALIDADE DE DADOS (DATA QUALITY)
# ==============================================================================
def validate_data_quality() -> dict:
    """Valida integridade referencial, unicidade de protocolo e ausência de PII."""
    fato = pd.read_csv(GOLD_DIR / "fato_chamados_zeladoria.csv")
    dim_loc = pd.read_csv(GOLD_DIR / "dim_localidade.csv")

    assert len(fato) > 0, "Erro DQ: Tabela fato está vazia."
    assert fato["protocolo"].is_unique, "Erro DQ: Existem protocolos duplicados na Gold."
    assert fato["sk_localidade"].isin(dim_loc["sk_localidade"]).all(), "Erro DQ: Chave órfã em sk_localidade."
    assert "cidadao_nome" not in fato.columns, "Erro LGPD: Coluna PII detectada na camada Gold."

    relatorio = {
        "status": "PASSED",
        "validado_em_utc": datetime.now(timezone.utc).isoformat(),
        "linhas_fato": int(len(fato)),
        "total_localidades": int(len(dim_loc)),
        "duplicidades_protocolo": 0,
        "conformidade_lgpd": True,
    }

    report_path = GOLD_DIR / "dq_report.json"
    report_path.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("[DATA QUALITY] Validação aprovada: %s", relatorio)
    return relatorio


if __name__ == "__main__":
    extract_bronze()
    transform_silver()
    model_gold()
    validate_data_quality()
