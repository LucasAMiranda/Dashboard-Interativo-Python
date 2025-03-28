import streamlit as slt
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

file_path = "EDB.csv"

# configurar a página
slt.set_page_config(page_title="Dashboard Financeiro", layout="wide")

# Adicionando CSS customizado para o cursor "mãozinha" nos selectboxes
slt.markdown(
    """
    <style>
    .streamlit-expanderHeader {
        cursor: pointer;
    }
    .stSelectbox select {
        cursor: pointer;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# título da Descrição do Dashboard
slt.title("📊 Dashboard Financeiro")
slt.markdown(
    """
    Bem-vindo ao Dashboard Financeiro!📈 
    Este painel interativo permite visualizar os dados econômicos e financeiros ao longo dos anos, 
    filtrando por região e métricas de interesse. Use filtros na Barra Lateral para explorar os dados.
    """
)

# carregar o dataset
df = pd.read_csv(file_path, sep=",")

# Limpeza dos Dados
df_columns = df.columns.str.strip()  # Remove espaços extras nos nomes das colunas
df = df.dropna(subset=["GeoFIPS", "GeoName", "Region", "Description"])  # Remove linhas com dados nulos
df.fillna(0, inplace=True)  # Substitui valores nulos por 0

# Renomear as colunas para português
df.rename(
    columns={
        "GeoFIPS": "Código Local",
        "GeoName": "Localidade",
        "Region": "Região",
        "TableName": "Tabela",
        "LineCode": "Código de Linha",
        "IndustryClassification": "Classificação Industrial",
        "Description": "Descrição",
        "Unit": "Unidade",
    },
    inplace=True
)

# Selecionar apenas as colunas principais para análise
df = df[["Código Local", "Localidade", "Região", "Descrição"] + [col for col in df.columns if col.isnumeric()]]

# Transformar os anos (colunas) em uma única coluna "Ano"
df = df.melt(id_vars=["Código Local", "Localidade", "Região", "Descrição"], var_name="Ano", value_name="Valor")

# Converter "Ano" para inteiro e tratar possíveis erros
df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce")
df.dropna(subset=["Ano"], inplace=True)
df["Ano"] = df["Ano"].astype(int)

# Converter "Valor" para número e substituir erros por 0
df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").fillna(0)

# Criar sidebar para filtros
slt.sidebar.header("Filtros de Análise")

# Selecionar o Ano (USANDO selectbox)
anos = sorted(df['Ano'].unique(), reverse=True)
ano_selecionado = slt.sidebar.selectbox("Selecione o Ano: ", anos)

# Selecionar por Região (USANDO selectbox)
regioes = df['Região'].unique()
regiao_selecionada = slt.sidebar.selectbox("Selecione a Região: ", regioes)

# Selecionar a Descrição (USANDO selectbox)
descricoes = df['Descrição'].unique()
descricao_selecionada = slt.sidebar.selectbox("Selecione a Métrica: ", descricoes)

# Filtrar os dados
filtered_df = df

# Aplicar filtro de ano
if ano_selecionado:
    filtered_df = filtered_df[filtered_df['Ano'] == ano_selecionado]

# Aplicar filtro de região
if regiao_selecionada:
    filtered_df = filtered_df[filtered_df['Região'] == regiao_selecionada]

# Aplicar filtro de descrição
if descricao_selecionada:
    filtered_df = filtered_df[filtered_df['Descrição'] == descricao_selecionada]

# Exibir a tabela filtrada
slt.subheader(f"Dados Filtrados - Ano: {ano_selecionado}, Região: {regiao_selecionada}")
slt.dataframe(filtered_df)

# Criar Gráficos
slt.subheader("📈 Análise Gráfica")

# Gráfico de Barras
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=filtered_df, x="Localidade", y="Valor", ax=ax, palette="Blues_r")
ax.set_title(f"{descricao_selecionada} por Localidade ({ano_selecionado})")
ax.set_xlabel("Localidade")
ax.set_ylabel("Valor")
plt.xticks(rotation=45)
slt.pyplot(fig)

# Gráfico de Pizza
slt.subheader("📊 Distribuição Percentual")
# Primeiro, somamos os valores por Localidade
localidades_valores = filtered_df.groupby("Localidade")["Valor"].sum()

# Verificar se algum valor é muito pequeno ou zero
localidades_valores = localidades_valores[localidades_valores > 0]

# Se ainda houver dados, gera o gráfico de pizza
if not localidades_valores.empty:
    fig, ax = plt.subplots(figsize=(7, 7))
    localidades_valores.plot(kind="pie", autopct="%1.1f%%", ax=ax, cmap="coolwarm")
    ax.set_title(f"Distribuição de {descricao_selecionada} por Localidade ({ano_selecionado})")
    slt.pyplot(fig)
else:
    slt.write("Não há dados suficientes para gerar o gráfico de pizza.")

# Gráfico de Linha - Evolução Temporal
slt.subheader("📈 Evolução ao Longo dos Anos")
df_evolucao = df[
    (df["Região"] == regiao_selecionada) & (df["Descrição"] == descricao_selecionada)
].groupby(["Ano"])["Valor"].sum().reset_index()
fig, ax = plt.subplots(figsize=(10, 5))
sns.lineplot(data=df_evolucao, x="Ano", y="Valor", marker="o", ax=ax)
ax.set_title(f"Evolução de {descricao_selecionada} ({regiao_selecionada})")
ax.set_xlabel("Ano")
ax.set_ylabel("Valor")
slt.pyplot(fig)

# Exibir o rodapé da página
slt.markdown("---")
slt.caption("📌 Dados extraídos de Economic Data Bureau (EDB) | Desenvolvido por Lucas Alencar Miranda")
