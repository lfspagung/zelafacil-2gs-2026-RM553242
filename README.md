# ZelaFácil — Plataforma Inteligente de Zeladoria Urbana e Acessibilidade.

> FIAP — Global Solution 2026.2 | Engenharia de Software (4º Ano - 4ESPR)  
> Autor: Lucas de Freitas Pagung | RM: 553242 - 4ESPR - AV. PAULISTA

---

## Ficha Técnica do MVP

Nome do Produto: ZelaFácil 

Cidadão e Território:

-Idosos, pessoas com deficiência (PcD) e moradores de bairros urbanos e periféricos que enfrentam barreiras de mobilidade e dificuldade de acesso a canais digitais burocráticos.

-Problema, em uma frase:** Problemas de manutenção urbana e falta de acessibilidade em pontos de ônibus e travessias demoram meses para serem resolvidos porque os canais públicos exigem cadastros complexos e dependem de triagem manual em sistemas legados.


-Proposta de Valor:** Plataforma web acessível onde o cidadão escaneia o QR Code de uma placa física tátil no espaço público, realiza o cadastro em 1 clique fotografando uma conta de consumo (OCR), relata o problema em linguagem simples com apoio de IA Generativa para geração de laudo técnico, e tem seu protocolo registrado automaticamente nos sistemas públicos via RPA.

-Arquitetura e Componentes:

  Produção (Cloud & DevOps):** Azure App Service (HTTPS) + GitHub Actions (CI/CD) + Application Insights (Monitoramento).

  Visão Computacional: Pipeline OpenCV + Tesseract OCR para detecção de bordas, correção de perspectiva e extração de endereço de faturas (Enel, Sabesp e Claro).

  Inteligência (GenAI): LLM com engenharia de prompt estruturada e *Human-in-the-Loop* para geração de laudo técnico baseado na norma ABNT NBR 9050.

  Dados (Big Data): Pipeline ETL orquestrado via Apache Airflow integrando dados abertos de zeladoria urbana e ocorrências georreferenciadas.

  Automação (RPA): Robô UiPath Studio para transferência autônoma de chamados validados para portais públicos legados sem API.

  Físico (Maker Lab):** Redesign de botoeira/placa informativa urbana com base em impressão 3D (STL) e frontal tátil/Braille + QR Code em corte a laser (SVG/DXF).

  Fontes de Dados:** Dados abertos de zeladoria municipal (Portal SP156 / IBGE) e base sintética de comprovantes de residência gerada para testes em conformidade com a LGPD.

  Modelos de IA Utilizados:** Tesseract OCR (visão computacional / extração textual) e GPT-4o-mini (classificação de severidade e laudo técnico NBR 9050).

URL do MVP e Repositório:
  MVP : `https://zelafacil-2gs-2026-RM553242.azurewebsites.net`
  Repositório: https://github.com/lfspagung/zelafacil-2gs-2026-RM553242.git

Indicadores de Impacto: Redução do tempo de cadastro de 8 minutos para 15 segundos; 95% dos chamados protocolados sem triagem manual; mapeamento de pontos críticos de acessibilidade por CEP.

ODS Conectados:

  ODS 10 (Redução das Desigualdades):** Elimina barreiras digitais e físicas para idosos e PcD acessarem serviços públicos essenciais.

  ODS 11 (Cidades e Comunidades Sustentáveis):** Promove espaços públicos urbanos mais seguros, inclusivos e acessíveis.
