ZelaFácil — Plataforma inteligente de zeladoria urbana e acessibilidade.

> FIAP — Global Solution 2026.2 | Engenharia de Software (4º Ano - 4ESPR)  
> Autor: Lucas de Freitas Pagung | RM: 553242 - 4ESPR - AV. PAULISTA

---
Aplicação em Produção (Microsoft Azure)

- URL oficial MVP (Azure App Service): [Acessar ZelaFácil no ar](https://zelafacil-2gs-2026-rm553242-sp-emfua5bbecfbbgeh.brazilsouth-01.azurewebsites.net)
- Infraestrutura: Azure App Service (Linux, Python 3.11, região Brazil South) com deploy contínuo via GitHub Actions.
- Inicialização automatizada: `startup.sh` (instalação do Tesseract OCR + execução do Streamlit na porta `8000`).
- Massa de testes OCR: utilize as faturas de demonstração disponíveis na pasta `faturas_teste/` deste repositório

> Nota para avaliação: Na primeira requisição após períodos de inatividade, o carregamento inicial pode levar alguns segundos devido ao *cold start* do contêiner Linux no Azure.

Repositório git: https://github.com/lfspagung/zelafacil-2gs-2026-RM553242.git

## Ficha Técnica do MVP:

Nome do Produto: ZelaFácil.

Cidadão e Território:

-Idosos, pessoas com deficiência (PcD) e moradores de bairros urbanos e periféricos que enfrentam barreiras de mobilidade e dificuldade de acesso a canais digitais burocráticos.

-Problema, em uma frase: Problemas de manutenção urbana e falta de acessibilidade em pontos de ônibus e travessias demoram meses para serem resolvidos porque os canais públicos exigem cadastros complexos e dependem de triagem manual em sistemas legados.


-Proposta de Valor: Plataforma web acessível onde o cidadão escaneia o QR Code de uma placa física tátil no espaço público, realiza o cadastro em 1 clique fotografando uma conta de consumo (OCR), relata o problema em linguagem simples com apoio de IA Generativa para geração de laudo técnico, e tem seu protocolo registrado automaticamente nos sistemas públicos via RPA.

-Arquitetura e Componentes:

  Produção (Cloud & DevOps): Azure App Service (HTTPS) + GitHub Actions (CI/CD) + Application Insights (Monitoramento).

  Visão Computacional: Pipeline OpenCV + Tesseract OCR para detecção de bordas, correção de perspectiva e extração de endereço de faturas (Enel, Sabesp e Claro).

  Inteligência (GenAI): LLM com engenharia de prompt estruturada e *Human-in-the-Loop* para geração de laudo técnico baseado na norma ABNT NBR 9050.

  Dados (Big Data): Pipeline ETL orquestrado via Apache Airflow integrando dados abertos de zeladoria urbana e ocorrências georreferenciadas.

  Automação (RPA): Robô UiPath Studio para transferência autônoma de chamados validados para portais públicos legados sem API.

  Físico (Maker Lab): Redesign de botoeira/placa informativa urbana com base em impressão 3D (STL) e frontal tátil/Braille + QR Code em corte a laser (SVG/DXF).

  Fontes de Dados: Dados abertos de zeladoria municipal (Portal SP156 / IBGE) e base sintética de comprovantes de residência gerada para testes em conformidade com a LGPD.

  Modelos de IA Utilizados: Tesseract OCR (visão computacional / extração textual) e GPT-4o-mini (classificação de severidade e laudo técnico NBR 9050).

---

## Dependências e Guia de Execução

Para executar o **ZelaFácil** localmente, são necessárias **7 bibliotecas Python** (declaradas em `mvp_app/requirements.txt`) e o motor de reconhecimento óptico **Tesseract OCR** instalado no sistema operacional.

### 1. Bibliotecas Python (`mvp_app/requirements.txt`)

| Biblioteca | Finalidade no Projeto |
| :--- | :--- |
| **`streamlit`** | Framework da interface web interativa, navegação em abas e controles de acessibilidade. |
| **`opencv-python-headless`** | Pré-processamento de imagem, detecção de contornos e retificação de perspectiva. |
| **`pytesseract`** | Interface Python para comunicação com o motor Tesseract OCR. |
| **`pillow`** | Leitura, conversão e manipulação de arquivos de imagem (`PNG`, `JPG`, `JPEG`). |
| **`numpy`** | Operações matriciais e cálculos geométricos do pipeline de visão computacional. |
| **`pandas`** | Estruturação da base de chamados validados e exportação da fila CSV para RPA. |
| **`openai`** | Cliente SDK utilizado na integração com a API OpenRouter / LLMs (com *fallback* local automático). |

---

2. Dependência de Sistema Operacional (Tesseract OCR)
Instale o binário do **Tesseract OCR** com o pacote de idioma **Português (`por`)** de acordo com o seu sistema:

macOS (via Homebrew):
 
  ```bash
  brew install tesseract tesseract-lang


Repositório: https://github.com/lfspagung/zelafacil-2gs-2026-RM553242.git

Indicadores de Impacto: Redução do tempo de cadastro de 8 minutos para 15 segundos; 95% dos chamados protocolados sem triagem manual; mapeamento de pontos críticos de acessibilidade por CEP.

ODS Conectados:

  ODS 10 (Redução das Desigualdades): Elimina barreiras digitais e físicas para idosos e PcD acessarem serviços públicos essenciais.

  ODS 11 (Cidades e Comunidades Sustentáveis): Promove espaços públicos urbanos mais seguros, inclusivos e acessíveis.
