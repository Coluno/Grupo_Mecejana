import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

# Configuração do título e imagem
st.set_page_config(page_title="Análise de Reservas da Pousada", layout="centered")
st.image("./logo.png", width=300)  # Adiciona a imagem da logo

# Carregar dados do arquivo Check-in.xls
data_file = "Check-in.xls"  # Certifique-se de que o arquivo esteja no mesmo diretório ou forneça o caminho correto
df = pd.read_excel(data_file)

# Seleção de colunas relevantes e tratamento dos dados
df_filtrado = df[["Entrada", "Saída", "Quartos", "Pessoas", "Preço", "Valor da comissão", "Duração (diárias)"]]
df_filtrado["Entrada"] = pd.to_datetime(df_filtrado["Entrada"])
df_filtrado["Saída"] = pd.to_datetime(df_filtrado["Saída"])
df_filtrado["Preço"] = df_filtrado["Preço"].str.replace(" BRL", "").astype(float)
df_filtrado["Valor da comissão"] = df_filtrado["Valor da comissão"].str.replace(" BRL", "").astype(float)
df_filtrado["Receita Líquida"] = df_filtrado["Preço"] - df_filtrado["Valor da comissão"]
df_filtrado["Mês"] = df_filtrado["Entrada"].dt.month

# Configuração do Streamlit
st.title("Análise de Reservas da Pousada")

# Sidebar
st.sidebar.title("Selecione uma análise")
analise = st.sidebar.radio("Escolha a análise desejada:", ["Análise Financeira", "Análise Temporal"])

# Análise Financeira
if analise == "Análise Financeira":
    st.header("Análise Financeira")
    
    # Selecionar intervalo de datas
    min_date = df_filtrado["Entrada"].min()
    max_date = df_filtrado["Entrada"].max()
    start_date, end_date = st.sidebar.date_input(
        "Selecione o intervalo de datas:",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    # Filtrar os dados com base nas datas selecionadas
    df_filtrado_data = df_filtrado[
        (df_filtrado["Entrada"] >= pd.to_datetime(start_date)) & 
        (df_filtrado["Entrada"] <= pd.to_datetime(end_date))
    ]
    
    # Gráfico de Receita Líquida por mês
    receita_liquida_mensal = df_filtrado_data.groupby("Mês")["Receita Líquida"].sum()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=receita_liquida_mensal.index,
        y=receita_liquida_mensal.values,
        text=[f"R$ {val:,.2f}" for val in receita_liquida_mensal.values],
        textposition="auto",
        marker_color="blue"
    ))
    fig.update_layout(
        title="Receita Líquida por Mês",
        xaxis_title="Mês",
        yaxis_title="Receita Líquida (R$)",
        template="plotly_white"
    )
    st.plotly_chart(fig)

# Análise Temporal
elif analise == "Análise Temporal":
    st.header("Análise Temporal")
    
    # Gráfico de número de reservas por mês
    reservas_por_mes = df_filtrado.groupby("Mês")["Entrada"].count()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=reservas_por_mes.index,
        y=reservas_por_mes.values,
        mode="lines+markers",
        line=dict(color="orange"),
        marker=dict(size=10),
        text=[f"{int(val)} reservas" for val in reservas_por_mes.values]
    ))
    fig.update_layout(
        title="Número de Reservas por Mês",
        xaxis_title="Mês",
        yaxis_title="Quantidade de Reservas",
        template="plotly_white"
    )
    st.plotly_chart(fig)
