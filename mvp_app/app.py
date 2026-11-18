import os
from datetime import datetime
import pandas as pd
from PIL import Image
import streamlit as st

from vision_ocr import extrair_dados_fatura
from genai_assistant import gerar_laudo_tecnico, responder_duvida_assistente, MODELOS_DISPONIVEIS

st.set_page_config(
    page_title="ZelaFácil — Zeladoria Urbana e Acessibilidade",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "alto_contraste" not in st.session_state:
    st.session_state.alto_contraste = False
if "fonte_grande" not in st.session_state:
    st.session_state.fonte_grande = False

CSV_CHAMADOS = "chamados_validados.csv"


def carregar_chamados() -> pd.DataFrame:
    if os.path.exists(CSV_CHAMADOS):
        return pd.read_csv(CSV_CHAMADOS)
    return pd.DataFrame(
        [
            {
                "protocolo": "ZF-2026-001",
                "data": "2026-11-15",
                "empresa_fatura": "Enel Distribuição",
                "endereco": "Rua General Francisco Glicério, 1020",
                "cep": "08674-000",
                "relato": "Botoeira sonora do semáforo sem resposta tátil na travessia.",
                "status": "Protocolado via RPA",
            }
        ]
    )


if st.session_state.alto_contraste:
    bg_page = "#0A0A0A"
    bg_surface = "#141414"
    bg_subtle = "#1F1F1F"
    border_color = "#FFD60A"
    text_primary = "#FFFFFF"
    text_secondary = "#E5E5E5"
    accent = "#FFD60A"
    accent_text = "#000000"
else:
    bg_page = "#F7F6F2"
    bg_surface = "#FFFFFF"
    bg_subtle = "#F0EFEA"
    border_color = "#E4E2DC"
    text_primary = "#18181B"
    text_secondary = "#52525B"
    accent = "#0F4C5C"
    accent_text = "#FFFFFF"

base_font = "18px" if st.session_state.fonte_grande else "15px"

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {{
    --bg-page: {bg_page};
    --bg-surface: {bg_surface};
    --bg-subtle: {bg_subtle};
    --border-color: {border_color};
    --text-primary: {text_primary};
    --text-secondary: {text_secondary};
    --accent: {accent};
    --accent-text: {accent_text};
}}

#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"] {{
    display: none !important;
    visibility: hidden !important;
}}

html, body, .stApp {{
    background-color: var(--bg-page) !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    font-size: {base_font} !important;
}}

.block-container {{
    max-width: 1040px !important;
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
}}

.zf-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 1.25rem;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid var(--border-color);
}}

.zf-brand {{
    display: flex;
    align-items: center;
    gap: 14px;
}}

.zf-logo {{
    width: 42px;
    height: 42px;
    border-radius: 10px;
    background-color: var(--accent);
    color: var(--accent-text);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}}

.zf-title {{
    font-size: 1.55rem;
    font-weight: 700;
    letter-spacing: -0.025em;
    color: var(--text-primary);
    margin: 0;
    line-height: 1.15;
}}

.zf-subtitle {{
    font-size: 0.88rem;
    color: var(--text-secondary);
    margin: 2px 0 0 0;
}}

.zf-meta-badge {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--text-secondary);
    background: var(--bg-subtle);
    border: 1px solid var(--border-color);
    padding: 5px 10px;
    border-radius: 6px;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 28px;
    border-bottom: 1px solid var(--border-color);
    background: transparent;
}}

.stTabs [data-baseweb="tab"] {{
    padding: 10px 2px 12px 2px;
    font-weight: 500;
    font-size: 0.96rem;
    color: var(--text-secondary);
    background: transparent !important;
    border: none !important;
}}

.stTabs [aria-selected="true"] {{
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    border-bottom: 2px solid var(--accent) !important;
}}

.stTabs [data-baseweb="tab-highlight"] {{
    background-color: var(--accent) !important;
}}

.zf-step {{
    display: flex;
    align-items: baseline;
    gap: 10px;
    margin: 1.75rem 0 0.75rem 0;
}}

.zf-step-num {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--accent-text);
    background: var(--accent);
    padding: 2px 8px;
    border-radius: 4px;
}}

.zf-step-title {{
    font-size: 1.1rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: var(--text-primary);
    margin: 0;
}}

.zf-helper {{
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin: -0.25rem 0 1rem 0;
    line-height: 1.5;
}}

.zf-card {{
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.25rem 1.4rem;
    margin-bottom: 1rem;
}}

[data-testid="stForm"] {{
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.4rem;
}}

.stTextInput input, .stTextArea textarea {{
    background-color: var(--bg-page) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    padding: 10px 12px !important;
}}

.stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(15, 76, 92, 0.14) !important;
}}

.stFormSubmitButton button, .stDownloadButton button {{
    background-color: var(--accent) !important;
    color: var(--accent-text) !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.65rem 1.4rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: opacity 0.15s ease;
}}

.stFormSubmitButton button:hover, .stDownloadButton button:hover {{
    opacity: 0.9 !important;
}}

.stButton button {{
    background-color: var(--bg-surface) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 7px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.35rem 0.75rem !important;
}}

[data-testid="stFileUploaderDropzone"] {{
    background: var(--bg-surface) !important;
    border: 1.5px dashed var(--border-color) !important;
    border-radius: 12px !important;
    padding: 1.2rem !important;
}}

.zf-kpi-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 1.2rem 0 1.6rem 0;
}}

.zf-kpi {{
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.15rem 1.3rem;
}}

.zf-kpi-label {{
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--text-secondary);
    margin-bottom: 6px;
}}

.zf-kpi-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.65rem;
    font-weight: 600;
    color: var(--text-primary);
    line-height: 1.2;
}}

.zf-kpi-sub {{
    font-size: 0.82rem;
    color: var(--text-secondary);
    margin-top: 4px;
}}

.zf-receipt {{
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-left: 4px solid var(--accent);
    border-radius: 10px;
    padding: 1.35rem 1.5rem;
    margin-top: 1.25rem;
}}

.zf-receipt-id {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: var(--accent);
    font-weight: 600;
}}

.zf-receipt-pre {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.84rem;
    background: var(--bg-subtle);
    color: var(--text-primary);
    padding: 1rem;
    border-radius: 8px;
    white-space: pre-wrap;
    margin-top: 0.75rem;
    line-height: 1.55;
}}

.zf-footer {{
    margin-top: 3rem;
    padding-top: 1.25rem;
    border-top: 1px solid var(--border-color);
    font-size: 0.8rem;
    color: var(--text-secondary);
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
}}

@media (max-width: 768px) {{
    .zf-kpi-grid {{ grid-template-columns: 1fr; }}
    .zf-header {{ flex-direction: column; align-items: flex-start; gap: 10px; }}
}}
</style>
""",
    unsafe_allow_html=True,
)

col_spacer, col_a1, col_a2 = st.columns([6.5, 1.8, 1.7])
with col_a1:
    lbl_fonte = "Texto padrão" if st.session_state.fonte_grande else "Ampliar texto (A+)"
    if st.button(lbl_fonte, use_container_width=True):
        st.session_state.fonte_grande = not st.session_state.fonte_grande
        st.rerun()
with col_a2:
    lbl_contraste = "Tema padrão" if st.session_state.alto_contraste else "Alto contraste"
    if st.button(lbl_contraste, use_container_width=True):
        st.session_state.alto_contraste = not st.session_state.alto_contraste
        st.rerun()

st.markdown(
    """
<div class="zf-header">
    <div class="zf-brand">
        <div class="zf-logo" aria-hidden="true">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                <circle cx="12" cy="10" r="3"></circle>
            </svg>
        </div>
        <div>
            <h1 class="zf-title">ZelaFácil</h1>
            <p class="zf-subtitle">Registro cidadão de zeladoria urbana e acessibilidade</p>
        </div>
    </div>
    <div class="zf-meta-badge">ODS 10 · ODS 11 · ABNT NBR 9050</div>
</div>
""",
    unsafe_allow_html=True,
)

aba_registro, aba_painel, aba_chat = st.tabs(["Nova ocorrência", "Painel territorial e fila RPA", "Assistente ZelaFácil (Chat IA)"])

with aba_registro:
    st.markdown(
        """
        <div class="zf-step">
            <span class="zf-step-num">01</span>
            <h2 class="zf-step-title">Leitura automática do comprovante</h2>
        </div>
        <p class="zf-helper">
            Envie uma foto ou imagem de conta de consumo (Enel, Sabesp ou Claro). O sistema corrige a perspectiva
            e preenche o endereço automaticamente para evitar digitação manual.
        </p>
        """,
        unsafe_allow_html=True,
    )

    arquivo = st.file_uploader(
        "Selecione o comprovante (PNG ou JPG)",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed",
    )

    dados_ocr = {"empresa_detectada": "", "logradouro": "", "cep": "", "bairro_cidade": "", "texto_ocr_bruto": ""}

    if arquivo:
        img = Image.open(arquivo)
        col_img, col_info = st.columns([1, 1.35], gap="large")
        with col_img:
            st.image(img, caption="Comprovante carregado", use_column_width=True)
        with col_info:
            with st.spinner("Analisando documento..."):
                dados_ocr = extrair_dados_fatura(img)

            st.markdown(
                f"""
                <div class="zf-card">
                    <div class="zf-kpi-label">Documento identificado</div>
                    <div style="font-size:1.15rem; font-weight:600; margin-bottom:10px;">
                        {dados_ocr['empresa_detectada']}
                    </div>
                    <div style="font-size:0.88rem; color:var(--text-secondary); line-height:1.6;">
                        <strong>Logradouro:</strong> {dados_ocr['logradouro'] or 'Não localizado'}<br>
                        <strong>CEP:</strong> {dados_ocr['cep'] or 'Não localizado'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.expander("Inspecionar texto bruto extraído pelo OCR"):
                st.code(dados_ocr.get("texto_ocr_bruto", "").strip() or "Sem texto retornado.")

    st.markdown(
        """
        <div class="zf-step">
            <span class="zf-step-num">02</span>
            <h2 class="zf-step-title">Conferência do endereço e relato do problema</h2>
        </div>
        <p class="zf-helper">
            Revise os dados lidos abaixo antes do envio. Seus dados são utilizados apenas para localizar a ocorrência
            junto ao serviço público, em conformidade com a LGPD.
        </p>
        """,
        unsafe_allow_html=True,
    )

    with st.form("form_ocorrencia"):
        c1, c2 = st.columns([2.2, 1])
        endereco = c1.text_input(
            "Logradouro e número",
            value=dados_ocr["logradouro"],
            placeholder="Ex.: Rua General Francisco Glicério, 1020",
        )
        cep = c2.text_input(
            "CEP",
            value=dados_ocr["cep"],
            placeholder="00000-000",
        )
        relato = st.text_area(
            "O que precisa de manutenção ou adequação neste local?",
            height=110,
            placeholder="Descreva com suas palavras. Ex.: Rampa da calçada quebrada dificultando a passagem de cadeira de rodas em frente ao ponto de ônibus.",
        )
        consentimento = st.checkbox(
            "Concordo com o uso deste endereço de forma anonimizada exclusivamente para abertura do chamado público (LGPD)."
        )
        enviado = st.form_submit_button("Registrar ocorrência e gerar parecer técnico")

    if enviado:
        if not endereco.strip() or not relato.strip() or not consentimento:
            st.warning("Informe o endereço, descreva o problema e confirme o termo de consentimento LGPD para continuar.")
        else:
            laudo = gerar_laudo_tecnico(relato.strip(), f"{endereco.strip()} - CEP {cep.strip()}")
            df = carregar_chamados()
            novo_id = f"ZF-2026-{len(df) + 1:03d}"
            novo_reg = pd.DataFrame(
                [
                    {
                        "protocolo": novo_id,
                        "data": datetime.now().strftime("%Y-%m-%d"),
                        "empresa_fatura": dados_ocr["empresa_detectada"] or "Preenchimento manual",
                        "endereco": endereco.strip(),
                        "cep": cep.strip(),
                        "relato": relato.strip(),
                        "status": "Na fila do robô RPA",
                    }
                ]
            )
            df = pd.concat([df, novo_reg], ignore_index=True)
            df.to_csv(CSV_CHAMADOS, index=False)

            st.markdown(
                f"""
                <div class="zf-receipt">
                    <div class="zf-receipt-id">PROTOCOLO {novo_id} · ENCAMINHADO PARA FILA RPA</div>
                    <div style="font-size:0.9rem; color:var(--text-secondary); margin-top:4px;">
                        Parecer técnico estruturado ({laudo['origem']})
                    </div>
                    <div class="zf-receipt-pre">{laudo['parecer']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

with aba_painel:
    df_atual = carregar_chamados()
    total_chamados = len(df_atual)
    em_fila = int((df_atual["status"] != "Protocolado via RPA").sum()) if "status" in df_atual.columns else 0

    st.markdown(
        f"""
        <div class="zf-kpi-grid">
            <div class="zf-kpi">
                <div class="zf-kpi-label">Ocorrências registradas</div>
                <div class="zf-kpi-value">{total_chamados}</div>
                <div class="zf-kpi-sub">Base integrada Airflow + MVP</div>
            </div>
            <div class="zf-kpi">
                <div class="zf-kpi-label">Aguardando robô UiPath</div>
                <div class="zf-kpi-value">{em_fila}</div>
                <div class="zf-kpi-sub">Prontos para envio ao portal 156</div>
            </div>
            <div class="zf-kpi">
                <div class="zf-kpi-label">Tempo médio de cadastro</div>
                <div class="zf-kpi-value">14s</div>
                <div class="zf-kpi-sub">Redução frente à triagem manual</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="zf-step-title" style="margin-bottom:0.75rem;">Fila operacional de chamados</div>', unsafe_allow_html=True)
    st.dataframe(df_atual, use_container_width=True, hide_index=True)

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    st.download_button(
        label="Exportar fila CSV para o UiPath Studio",
        data=df_atual.to_csv(index=False).encode("utf-8"),
        file_name="fila_chamados_rpa.csv",
        mime="text/csv",
    )

with aba_chat:
    st.markdown('<div class="zf-step"><span class="zf-step-num">IA</span><h2 class="zf-step-title">Assistente de Dúvidas e Suporte ao Cidadão</h2></div>', unsafe_allow_html=True)
    modelo_escolhido = st.selectbox("Modelo de Linguagem (OpenRouter / LLM)", options=MODELOS_DISPONIVEIS, index=0)
    if "historico_chat" not in st.session_state:
        st.session_state.historico_chat = [{"role": "assistant", "origem": "Sistema ZelaFácil", "dados": {"topico": "Boas-vindas", "resposta": "Olá! Pergunte como enviar sua conta, como funciona a LGPD ou como ativar acessibilidade.", "passo_sugerido": "Digite abaixo.", "confianca": "ALTA"}}]
    q = st.chat_input("Escreva sua dúvida sobre o ZelaFácil...")
    if q:
        st.session_state.historico_chat.append({"role": "user", "texto": q})
        r = responder_duvida_assistente(q, modelo=modelo_escolhido)
        st.session_state.historico_chat.append({"role": "assistant", "origem": r["origem"], "dados": r["dados"]})
    for idx, m in enumerate(st.session_state.historico_chat):
        if m["role"] == "user":
            st.chat_message("user").write(m["texto"])
        else:
            with st.chat_message("assistant"):
                d = m["dados"]
                st.markdown(f"**[{d.get('topico')}]** {d.get('resposta')}")
                st.caption(f"Próximo passo: {d.get('passo_sugerido')} · Motor: {m.get('origem')}")
                with st.expander(f"JSON #{idx+1}"):
                    st.json(d)
st.markdown(
    """
<div class="zf-footer">
    <span>ZelaFácil (zelafacil-2gs-2026-RM553242) · Engenharia de Software 4ES</span>
    <span>Lucas de Freitas Pagung · RM 553242 · FIAP Global Solution 2026.2</span>
</div>
""",
    unsafe_allow_html=True,
)
