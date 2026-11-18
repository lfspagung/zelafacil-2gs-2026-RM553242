import os, json
from openai import OpenAI

CONTEXTO = """Você é o Assistente Oficial do ZelaFácil (zelafacil-2gs-2026-RM553242), plataforma CitizenTech de zeladoria urbana e acessibilidade (FIAP 4ES - Lucas de Freitas Pagung, RM 553242).
Funcionalidades: 1) OCR de contas Enel, Sabesp e Claro (PNG/JPG) no Passo 01; 2) Revisão manual e consentimento LGPD no Passo 02; 3) Laudo técnico ABNT NBR 9050 em JSON; 4) Fila RPA CSV para portal 156; 5) Botões A+ e Alto Contraste no topo direito.
Erros comuns: 'Concessionária Não identificada' (foto desfocada ou outra empresa -> digitar no Passo 02); 'Logradouro não localizado' (foto cortada -> digitar manualmente)."""

MODELOS_DISPONIVEIS = ["openai/gpt-4o-mini", "google/gemini-2.0-flash-001", "meta-llama/llama-3.1-8b-instruct"]

def _cliente():
    k = os.getenv("OPENROUTER_API_KEY")
    if k:
        return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=k), "OpenRouter API"
    if os.getenv("OPENAI_API_KEY"):
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY")), "OpenAI API"
    return None, "Fallback Determinístico Local"

def _parse_json(txt):
    t = txt.strip()
    if t.startswith("```"):
        t = "\n".join([l for l in t.splitlines() if not l.strip().startswith("```")]).strip()
    return json.loads(t)

def gerar_laudo_tecnico(relato_cidadao: str, endereco: str, modelo: str = "openai/gpt-4o-mini") -> dict:
    cli, prov = _cliente()
    sys = 'Engenheiro especialista ABNT NBR 9050. Retorne APENAS JSON com chaves: "categoria", "gravidade" ("ALTA"|"MEDIA"|"BAIXA"), "norma_aplicavel", "parecer_tecnico", "acao_recomendada".'
    if cli:
        try:
            r = cli.chat.completions.create(model=modelo, messages=[{"role":"system","content":sys},{"role":"user","content":f"Endereço: {endereco}\nRelato: {relato_cidadao}"}], temperature=0.2, response_format={"type":"json_object"})
            d = _parse_json(r.choices[0].message.content)
            if {"categoria","gravidade","norma_aplicavel","parecer_tecnico","acao_recomendada"}.issubset(d.keys()):
                return {"origem": f"{prov} ({modelo})", "json_estruturado": d, "parecer": f"CATEGORIA: {d['categoria']}\nGRAVIDADE: {d['gravidade']}\nNORMA: {d['norma_aplicavel']}\nPARECER: {d['parecer_tecnico']}\nAÇÃO: {d['acao_recomendada']}"}
        except Exception:
            pass
    rl = relato_cidadao.lower()
    if any(p in rl for p in ["buraco","calçada","calcada","rampa","cadeirante"]):
        d = {"categoria":"Acessibilidade em Passeio Público","gravidade":"ALTA","norma_aplicavel":"ABNT NBR 9050 - Seção 6.12","parecer_tecnico":f"Obstrução no passeio em {endereco}: '{relato_cidadao}'.","acao_recomendada":"Nivelamento emergencial da faixa livre."}
    elif any(p in rl for p in ["semáforo","semaforo","botoeira","ônibus","onibus","ponto"]):
        d = {"categoria":"Sinalização Viária e Transporte","gravidade":"ALTA","norma_aplicavel":"ABNT NBR 9050 - Seção 5.4","parecer_tecnico":f"Falha em travessia/embarque em {endereco}: '{relato_cidadao}'.","acao_recomendada":"Manutenção imediata da sinalização tátil/sonora."}
    else:
        d = {"categoria":"Zeladoria Urbana","gravidade":"MEDIA","norma_aplicavel":"Lei 13.146/2015","parecer_tecnico":f"Não conformidade em {endereco}: '{relato_cidadao}'.","acao_recomendada":"Vistoria e reparo municipal."}
    return {"origem": "Motor Técnico Estruturado (Fallback)", "json_estruturado": d, "parecer": f"CATEGORIA: {d['categoria']}\nGRAVIDADE: {d['gravidade']}\nNORMA: {d['norma_aplicavel']}\nPARECER: {d['parecer_tecnico']}\nAÇÃO: {d['acao_recomendada']}"}

def responder_duvida_assistente(pergunta_usuario: str, modelo: str = "openai/gpt-4o-mini") -> dict:
    cli, prov = _cliente()
    sys = f'{CONTEXTO}\nResponda APENAS JSON válido com chaves: "topico", "resposta", "passo_sugerido", "confianca".'
    if cli:
        try:
            r = cli.chat.completions.create(model=modelo, messages=[{"role":"system","content":sys},{"role":"user","content":pergunta_usuario}], temperature=0.3, response_format={"type":"json_object"})
            d = _parse_json(r.choices[0].message.content)
            if {"topico","resposta","passo_sugerido","confianca"}.issubset(d.keys()):
                return {"origem": f"{prov} ({modelo})", "dados": d}
        except Exception:
            pass
    q = pergunta_usuario.lower()
    if any(k in q for k in ["fatura","conta","enel","sabesp","claro","ocr","não identificada"]):
        d = {"topico":"Faturas e OCR","resposta":"Aceitamos faturas Enel, Sabesp ou Claro (PNG/JPG). Se der erro, preencha o endereço manualmente no Passo 02.","passo_sugerido":"Vá para Nova ocorrência > Passo 01 ou 02.","confianca":"ALTA"}
    elif any(k in q for k in ["contraste","letra","fonte","acessibilidade"]):
        d = {"topico":"Acessibilidade","resposta":"Use os botões 'Ampliar texto (A+)' e 'Alto contraste' no topo direito da tela.","passo_sugerido":"Clique nos botões superiores direitos.","confianca":"ALTA"}
    elif any(k in q for k in ["lgpd","dados","privacidade"]):
        d = {"topico":"LGPD","resposta":"Usamos apenas logradouro e CEP anonimizados mediante seu consentimento explícito.","passo_sugerido":"Marque a caixa LGPD antes de enviar.","confianca":"ALTA"}
    else:
        d = {"topico":"Como usar","resposta":"1) Envie a conta no Passo 01; 2) Revise o endereço e descreva o problema no Passo 02; 3) Aceite a LGPD e registre.","passo_sugerido":"Comece pelo Passo 01.","confianca":"ALTA"}
    return {"origem": "Assistente Contextual Local (Fallback)", "dados": d}
