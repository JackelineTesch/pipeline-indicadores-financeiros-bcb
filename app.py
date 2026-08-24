# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ── Configuração da página ──────────────────────────────────────────
st.set_page_config(
    page_title="Indicadores Financeiros — BACEN",
    page_icon="📊",
    layout="wide"
)

# ── Estilo customizado ──────────────────────────────────────────────
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    .metric-card {
        background-color: #1E2130;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00D4FF;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #AAAAAA;
    }
    </style>
""", unsafe_allow_html=True)


# ── Carregar dados ──────────────────────────────────────────────────
@st.cache_data(ttl=3600)  # atualiza o cache a cada 1 hora
def carregar_dados():
    url = "https://raw.githubusercontent.com/JackelineTesch/pipeline-indicadores-financeiros-bcb/main/data/processed/indicadores_atual.csv"
    df = pd.read_csv(url)
    df["data"] = pd.to_datetime(df["data"])
    return df


# ── Valor mais recente por indicador ───────────────────────────────
def valor_mais_recente(df, indicador):
    filtrado = df[df["indicador"] == indicador]
    ultima_data = filtrado["data"].max()
    valor = filtrado[filtrado["data"] == ultima_data]["valor"].values[0]
    return valor, ultima_data


# ── Início do app ──────────────────────────────────────────────────
df = carregar_dados()

# Título
st.markdown("## 📊 Indicadores Econômicos — Banco Central do Brasil")
st.markdown("Dados extraídos automaticamente via API pública do BACEN · Atualização diária")
st.divider()

# ── KPIs ───────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

selic, data_selic = valor_mais_recente(df, "selic")
cdi, data_cdi = valor_mais_recente(df, "cdi")
ipca, data_ipca = valor_mais_recente(df, "ipca")
cambio, data_cambio = valor_mais_recente(df, "cambio_dolar")

# Anualização: (1 + taxa diária) ^ 252 - 1
selic_anual = ((1 + selic / 100) ** 252 - 1) * 100
cdi_anual = ((1 + cdi / 100) ** 252 - 1) * 100

with col1:
    st.metric(
        label="🏦 SELIC (% a.a.)",
        value=f"{selic_anual:.2f}%",
        delta=f"Ref: {data_selic.strftime('%d/%m/%Y')}"
    )

with col2:
    st.metric(
        label="💰 CDI (% a.a.)",
        value=f"{cdi_anual:.2f}%",
        delta=f"Ref: {data_cdi.strftime('%d/%m/%Y')}"
    )

with col3:
    st.metric(
        label="📈 IPCA (% a.m.)",
        value=f"{ipca:.2f}%",
        delta=f"Ref: {data_ipca.strftime('%m/%Y')}"
    )

with col4:
    st.metric(
        label="💵 Câmbio USD/BRL",
        value=f"R$ {cambio:.4f}",
        delta=f"Ref: {data_cambio.strftime('%d/%m/%Y')}"
    )

st.markdown("<br>", unsafe_allow_html=True)
st.divider()
st.markdown("<br>", unsafe_allow_html=True)

# ── Filtros ────────────────────────────────────────────────────────
col_f1, col_f2 = st.columns([2, 1])

with col_f1:
    anos = sorted(df["ano"].unique())
    ano_range = st.slider(
        "Período de análise",
        min_value=int(anos[0]),
        max_value=int(anos[-1]),
        value=(int(anos[0]), int(anos[-1]))
    )

with col_f2:
    indicadores_opcoes = {
        "SELIC": "selic",
        "CDI": "cdi",
        "IPCA": "ipca",
        "Câmbio USD/BRL": "cambio_dolar"
    }
    selecionados = st.multiselect(
        "Indicadores",
        options=list(indicadores_opcoes.keys()),
        default=["SELIC", "CDI", "IPCA"]
    )

st.divider()

# ── Filtrar dados ──────────────────────────────────────────────────
codigos_selecionados = [indicadores_opcoes[s] for s in selecionados]
df_filtrado = df[
    (df["ano"] >= ano_range[0]) &
    (df["ano"] <= ano_range[1]) &
    (df["indicador"].isin(codigos_selecionados))
]

# ── Gráfico de linha: Evolução histórica ───────────────────────────
if not df_filtrado.empty:

    # Opção de sobrepor média móvel
    mostrar_media_movel = st.toggle(
        "📈 Sobrepor Média Móvel 30 dias",
        value=True
    )

    fig_linha = px.line(
        df_filtrado,
        x="data",
        y="valor",
        color="indicador",
        title="Evolução Histórica dos Indicadores",
        labels={"data": "Data", "valor": "Valor", "indicador": "Indicador"},
        template="plotly_dark"
    )

    # Adiciona média móvel apenas para IPCA (único onde é visualmente relevante)
    if mostrar_media_movel and "ipca" in codigos_selecionados:
        df_ipca = df_filtrado[df_filtrado["indicador"] == "ipca"].copy()
        fig_linha.add_scatter(
            x=df_ipca["data"],
            y=df_ipca["media_movel_30d"],
            mode="lines",
            line=dict(dash="dash", width=1.5, color="#FFD700"),
            name="IPCA (MM30)",
            opacity=0.8
        )

    fig_linha.update_layout(
        height=400,
        legend_title="Indicador",
        hovermode="x unified"
    )
    st.plotly_chart(fig_linha, use_container_width=True)
else:
    st.warning("Nenhum indicador selecionado.")

# ── Gráfico de variação acumulada anual ───────────────────────────
st.markdown("### 📉 Variação Acumulada por Ano")

df_var_anual = (
    df_filtrado.groupby(["ano", "indicador"])["valor"]
    .agg(["first", "last"])
    .reset_index()
)
df_var_anual["variacao_anual_pct"] = (
    (df_var_anual["last"] - df_var_anual["first"])
    / df_var_anual["first"] * 100
).round(2)

fig_var_anual = px.bar(
    df_var_anual,
    x="ano",
    y="variacao_anual_pct",
    color="indicador",
    barmode="group",
    title="Variação Acumulada Anual por Indicador (%)",
    labels={
        "ano": "Ano",
        "variacao_anual_pct": "Variação (%)",
        "indicador": "Indicador"
    },
    template="plotly_dark"
)
fig_var_anual.update_layout(
    height=350,
    legend_title="Indicador",
    hovermode="x unified"
)
fig_var_anual.add_hline(
    y=0,
    line_dash="dash",
    line_color="white",
    opacity=0.3
)
st.plotly_chart(fig_var_anual, use_container_width=True)

# ── Gráficos lado a lado ───────────────────────────────────────────
col_g1, col_g2 = st.columns(2)

with col_g1:
    # Média anual
    df_media = df_filtrado.groupby(
        ["ano", "indicador"])["valor"].mean().reset_index()
    df_media.columns = ["ano", "indicador", "media_valor"]

    fig_barra = px.bar(
        df_media,
        x="ano",
        y="media_valor",
        color="indicador",
        barmode="group",
        title="Média Anual por Indicador",
        labels={"ano": "Ano", "media_valor": "Média", "indicador": "Indicador"},
        template="plotly_dark"
    )
    fig_barra.update_layout(height=350)
    st.plotly_chart(fig_barra, use_container_width=True)

with col_g2:
    # Câmbio separado
    df_cambio = df[
        (df["indicador"] == "cambio_dolar") &
        (df["ano"] >= ano_range[0]) &
        (df["ano"] <= ano_range[1])
    ]
    fig_cambio = px.line(
        df_cambio,
        x="data",
        y="valor",
        title="Evolução do Câmbio — USD/BRL",
        labels={"data": "Data", "valor": "R$"},
        template="plotly_dark",
        color_discrete_sequence=["#00D4FF"]
    )
    fig_cambio.update_layout(height=350)
    st.plotly_chart(fig_cambio, use_container_width=True)

# ── Tabela de dados ────────────────────────────────────────────────
st.divider()
with st.expander("📋 Ver dados brutos"):
    st.dataframe(
        df_filtrado[["data", "indicador", "valor", "media_movel_30d", "variacao_pct"]]
        .sort_values(["indicador", "data"], ascending=[True, False])
        .reset_index(drop=True),
        use_container_width=True
    )

# ── Rodapé ─────────────────────────────────────────────────────────
st.divider()
st.markdown("""
    <div style='text-align: center; color: #666666; font-size: 0.8rem;'>
    Fonte: Banco Central do Brasil (BACEN) — API SGS |
    Desenvolvido por <strong>Jackeline Tesch</strong> |
    <a href='https://linkedin.com/in/jackelinestesch' target='_blank'>LinkedIn</a> ·
    <a href='https://github.com/JackelineTesch' target='_blank'>GitHub</a>
    </div>
""", unsafe_allow_html=True)