# dashboard.py

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURAÇÃO BÁSICA DA PÁGINA ---
st.set_page_config(
    page_title="Dashboard de Falhas de Software",
    layout="wide"
)

st.title("Dashboard de Falhas de Software")

# --- CARREGAMENTO DOS DADOS COM CACHE ---
@st.cache_data
def load_data():
    # Substitua pelos nomes corretos dos seus arquivos, se necessário
    df_csv = pd.read_csv("dados_falhas_software (1).csv")
    df_excel = pd.read_excel("resultado_falhas_com_previsao.xlsx")
    return df_csv, df_excel

df_csv, df_excel = load_data()

# --- SIDEBAR: FILTROS ---
st.sidebar.header("Filtros")
# Filtro para CSV por empresa
empresas_csv = df_csv["empresa"].unique().tolist()
empresa_selecionada = st.sidebar.multiselect(
    "Selecione empresa(s) (CSV)",
    options=empresas_csv,
    default=empresas_csv
)
df_csv_filtrado = df_csv[df_csv["empresa"].isin(empresa_selecionada)]

# Filtro para Excel por empresa
empresas_excel = df_excel["empresa"].unique().tolist()
empresa_excel_sel = st.sidebar.multiselect(
    "Selecione empresa(s) (Excel)",
    options=empresas_excel,
    default=empresas_excel
)
df_excel_filtrado = df_excel[df_excel["empresa"].isin(empresa_excel_sel)]


# --- GRÁFICO 1: TOTAL DE FALHAS POR EMPRESA (CSV) ---
st.header("1) Total de Falhas por Empresa (CSV)")
failures_by_empresa = (
    df_csv_filtrado
    .groupby("empresa")["num_falhas"]
    .sum()
    .reset_index()
    .sort_values("num_falhas", ascending=False)
)
fig1 = px.bar(
    failures_by_empresa,
    x="empresa",
    y="num_falhas",
    labels={"empresa": "Empresa", "num_falhas": "Número de Falhas"},
    title="Total de Falhas por Empresa"
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")


# --- GRÁFICO 2: LINHAS DE CÓDIGO VS NÚMERO DE FALHAS (CSV) ---
st.header("2) Linhas de Código vs Número de Falhas (CSV)")
fig2 = px.scatter(
    df_csv_filtrado,
    x="linhas_codigo",
    y="num_falhas",
    color="complexidade",
    hover_data=["empresa", "modulo"],
    labels={
        "linhas_codigo": "Linhas de Código",
        "num_falhas": "Número de Falhas",
        "complexidade": "Complexidade"
    },
    title="Linhas de Código vs Número de Falhas"
)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")


# --- GRÁFICO 3: CONTAGEM DE COMPONENTES POR PREVISÃO DE FALHA (Excel) ---
st.header("3) Contagem por Previsão de Falha (Excel)")
predictions_count = (
    df_excel_filtrado["previsao_falha"]
    .value_counts()
    .sort_index()
    .reset_index()
)
predictions_count.columns = ["previsao_falha", "count"]
fig3 = px.bar(
    predictions_count,
    x="previsao_falha",
    y="count",
    labels={"previsao_falha": "Previsão de Falha (0=Não, 1=Sim)", "count": "Contagem"},
    title="Quantos Componentes Prevêem Falha"
)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")


# --- GRÁFICO 4: CONTAGEM DE COMPONENTES COM FALHA (REAL) (Excel) ---
st.header("4) Contagem por Falha Real (Excel)")
actual_count = (
    df_excel_filtrado["possui_falha"]
    .value_counts()
    .sort_index()
    .reset_index()
)
actual_count.columns = ["possui_falha", "count"]
fig4 = px.bar(
    actual_count,
    x="possui_falha",
    y="count",
    labels={"possui_falha": "Falha Real (0=Não, 1=Sim)", "count": "Contagem"},
    title="Quantos Componentes Tiveram Falha de Fato"
)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")


# --- TABELA 5: COMPONENTES COM PREVISÃO INCORRETA DE FALHA (Excel) ---
st.header("5) Componentes com Previsão Incorreta de Falha")
mismatches = df_excel_filtrado[
    df_excel_filtrado["previsao_falha"] != df_excel_filtrado["possui_falha"]
][["componente_id", "empresa", "modulo", "possui_falha", "previsao_falha"]]

if mismatches.empty:
    st.success("Nenhuma discrepância encontrada entre previsão e real.")
else:
    st.dataframe(
        mismatches.rename(
            columns={
                "componente_id": "ID Componente",
                "empresa": "Empresa",
                "modulo": "Módulo",
                "possui_falha": "Falha Real",
                "previsao_falha": "Falha Prevista"
            }
        ),
        use_container_width=True,
        height=300
    )

st.markdown("#")  # espaço extra


# --- VISÕES ADICIONAIS “ÓBVIAS” QUE SEMPRE RETORNAM DADOS ---

# 6) DISTRIBUIÇÃO DE COMPLEXIDADE (CSV)
st.header("6) Distribuição de Complexidade (CSV)")
complex_count = (
    df_csv_filtrado["complexidade"]
    .value_counts()
    .reset_index()
)
complex_count.columns = ["complexidade", "count"]
fig6 = px.bar(
    complex_count,
    x="complexidade",
    y="count",
    labels={"complexidade": "Complexidade", "count": "Frequência"},
    title="Contagem de Componentes por Nível de Complexidade"
)
st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")


# 7) MÉDIA DE FALHAS POR COMPLEXIDADE (CSV)
st.header("7) Média de Falhas por Complexidade (CSV)")
avg_failures = (
    df_csv_filtrado
    .groupby("complexidade")["num_falhas"]
    .mean()
    .reset_index()
    .sort_values("complexidade")
)
fig7 = px.bar(
    avg_failures,
    x="complexidade",
    y="num_falhas",
    labels={"complexidade": "Complexidade", "num_falhas": "Média de Falhas"},
    title="Média de Falhas por Complexidade"
)
st.plotly_chart(fig7, use_container_width=True)

st.markdown("---")


# 8) CONTAGEM DE COMPONENTES POR MÓDULO (CSV)
st.header("8) Contagem de Componentes por Módulo (CSV)")
module_count = (
    df_csv_filtrado["modulo"]
    .value_counts()
    .reset_index()
)
module_count.columns = ["modulo", "count"]
fig8 = px.bar(
    module_count,
    x="modulo",
    y="count",
    labels={"modulo": "Módulo", "count": "Contagem"},
    title="Número de Componentes por Módulo"
)
st.plotly_chart(fig8, use_container_width=True)

st.markdown("---")


# 9) TAXA DE ACERTO DA PREVISÃO (Excel)
st.header("9) Taxa de Acerto da Previsão (Excel)")
total_registros = len(df_excel_filtrado)
if total_registros > 0:
    corretos = len(df_excel_filtrado[
        df_excel_filtrado["previsao_falha"] == df_excel_filtrado["possui_falha"]
    ])
    taxa = round(100 * corretos / total_registros, 2)
else:
    taxa = 0.0

st.metric(label="Taxa de acerto (%)", value=f"{taxa} %")

st.markdown("---")


# --- SEÇÃO EXTRA: EXIBIÇÃO DOS DADOS BRUTOS EXPANSÍVEIS ---
with st.expander("Exibir dados brutos (CSV)"):
    st.dataframe(df_csv_filtrado, use_container_width=True)

with st.expander("Exibir dados brutos (Excel)"):
    st.dataframe(df_excel_filtrado, use_container_width=True)
