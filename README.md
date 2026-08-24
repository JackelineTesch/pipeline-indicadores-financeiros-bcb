# 📊 Pipeline de Indicadores Financeiros — Banco Central do Brasil

Pipeline de dados automatizado que extrai, transforma e carrega indicadores
econômicos da API pública do BACEN, com visualizações em Power BI e Streamlit.

---

## 🎯 Problema de Negócio

Analistas financeiros precisam acompanhar diariamente a evolução de indicadores
como SELIC, IPCA, CDI e Câmbio. Fazer isso manualmente — acessando o site do
BACEN, copiando dados, colando em planilhas — consome tempo e gera inconsistências.

Este pipeline automatiza todo esse processo: extrai os dados diretamente da API
oficial, transforma e enriquece com métricas calculadas, carrega em banco analítico
e disponibiliza em duas visualizações complementares — um dashboard executivo no
Power BI e uma aplicação interativa de análise em Streamlit.

---

## 🏗️ Arquitetura da Solução

```
API BACEN (SGS)
      │
      ▼
 [EXTRACT]  src/extract.py
 Coleta dados dos últimos 5 anos via requests
 Salva CSV bruto em data/raw/
      │
      ▼
 [TRANSFORM]  src/transform.py
 Limpeza, enriquecimento e cálculo de métricas
 Salva CSV processado em data/processed/
      │
      ▼
 [LOAD]  src/load.py
 Carga no DuckDB com validação de integridade
 Banco analítico em data/processed/
      │
      ├─────────────────────┐
      ▼                     ▼
 [POWER BI]           [STREAMLIT]
 Dashboard executivo  App interativo
 Visão corporativa    Análise dinâmica
```

---

## 📈 Indicadores Extraídos

| Indicador | Código BACEN | Frequência |
|---|---|---|
| SELIC | 11 | Diária |
| CDI | 12 | Diária |
| IPCA | 433 | Mensal |
| Câmbio Dólar (PTAX) | 1 | Diária |

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.x |
| Extração | requests |
| Transformação | Pandas |
| Banco de Dados | DuckDB |
| Conexão BD | SQLAlchemy |
| Variáveis de Ambiente | python-dotenv |
| Versionamento | Git / GitHub |
| Dashboard Executivo | Power BI |
| App Interativo | Streamlit |

---

## 📊 Visualizações

| Ferramenta | Tipo | Público-alvo | Link |
|---|---|---|---|
| Power BI | Dashboard executivo corporativo | Diretoria e gestores financeiros | [📄 Ver dashboard](dashboard_indicadores.pdf) |
| Streamlit | Aplicação interativa de análise | Analistas e equipes técnicas | Em breve |

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.10+
- Git

### Instalação

```bash
# Clone o repositório
git clone https://github.com/JackelineTesch/pipeline-indicadores-financeiros-bcb.git
cd pipeline-indicadores-financeiros-bcb

# Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
```

### Execução do Pipeline

```bash
python pipeline.py
```

### Execução do App Streamlit

```bash
streamlit run app.py
```

---

## 📁 Estrutura do Projeto

```
pipeline-indicadores-financeiros-bcb/
│
├── data/
│   ├── raw/              ← dados brutos da API (não versionados)
│   └── processed/        ← dados transformados (não versionados)
│
├── src/
│   ├── extract.py        ← extração da API do BACEN
│   ├── transform.py      ← limpeza e enriquecimento
│   └── load.py           ← carga no DuckDB
│
├── app.py                ← aplicação Streamlit
├── pipeline.py           ← orquestrador principal
├── requirements.txt      ← dependências do projeto
├── .env.example          ← modelo de variáveis de ambiente
└── README.md
```

---

## 👩‍💻 Autora

**Jackeline Tesch**
Engenheira de Dados | Python · SQL · ETL · Power BI · Streamlit · DuckDB

[![LinkedIn](https://img.shields.io/badge/LinkedIn-jackelinestesch-blue?logo=linkedin)](https://linkedin.com/in/jackelinestesch)
[![GitHub](https://img.shields.io/badge/GitHub-portfolio-black?logo=github)](https://github.com/JackelineTesch)
