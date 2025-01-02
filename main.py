import numpy as np
import pandas as pd
import yfinance as yf
import plotly.express as px
import streamlit as st
from scipy.stats import norm

# Função para calcular o modelo Jump-Diffusion
def modelo_jump_diffusion(symbol, start_date, sigma=None, jump_intensity=0.01, jump_mean=0.02, jump_vol=0.1, T=1, steps=252):
    # Baixar dados históricos do ativo
    data = yf.download(symbol, start=start_date, end="2024-01-01")
    data.reset_index(inplace=True)
    data.set_index('Date', inplace=True)

    # Cálculos de retornos diários
    data['Log Returns'] = np.log(data['Adj Close'] / data['Adj Close'].shift(1))
    
    # Calcular a volatilidade histórica, se sigma não for fornecido
    if sigma is None:
        sigma = data['Log Returns'].std()  # Volatilidade histórica (desvio padrão dos retornos diários)

    # Parâmetros do modelo
    mu = data['Log Returns'].mean()  # Taxa de retorno média
    dt = T / steps  # Tamanho do intervalo de tempo

    # Inicializando os preços simulados
    S0 = data['Adj Close'][-1]  # Preço inicial
    prices = [S0]
    
    # Simulação do preço com o modelo Jump-Diffusion
    for _ in range(steps):
        # Difusão Browniana
        dW = np.random.normal(0, 1) * np.sqrt(dt)
        # Saltos
        jump = np.random.poisson(jump_intensity) * np.random.normal(jump_mean, jump_vol)
        
        # Cálculo do preço no próximo passo
        S_t = prices[-1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * dW + jump)
        prices.append(S_t)
    
    data['Simulated Price'] = prices[:len(data)]  # Preço simulado

    # Gráfico de preço simulado
    fig = px.line(data, x=data.index, y=['Adj Close', 'Simulated Price'], title=f"Simulação Jump-Diffusion - {symbol}")
    st.plotly_chart(fig)

    return data

# Função principal para Streamlit
def volatilidade_jump_diffusion():
    # Configuração da interface do usuário
    st.title("Simulação de Preços - Modelo Jump-Diffusion")

    # Seleção da variável a ser estudada
    variable = st.selectbox("Escolha a variável para estudar:", ["Açúcar", "Dólar"])

    # Seleção da data de início
    start_date = st.date_input("Selecione a data de início:", value=pd.to_datetime("2013-01-01"))

    # Definindo o símbolo com base na variável escolhida
    symbol = "SB=F" if variable == "Açúcar" else "USDBRL=X"

    # Entrada do usuário para sigma (volatilidade), que pode ser deixado em branco para usar a volatilidade histórica
    sigma_input = st.text_input("Digite o valor de sigma (volatilidade):", value="")

    # Se o usuário não inserir o valor de sigma, utilizar a volatilidade histórica
    sigma = float(sigma_input) if sigma_input else None

    # Botão para iniciar a simulação
    if st.button("Simular"):
        # Obtenção dos dados históricos e simulação do modelo Jump-Diffusion
        data = modelo_jump_diffusion(symbol, start_date.strftime('%Y-%m-%d'), sigma)

        # Exibindo o gráfico de preços simulados
        st.subheader(f"Simulação de Preços - {variable}")
        if sigma is None:
            st.write(f"A volatilidade utilizada (sigma) foi calculada com base nos dados históricos do ativo.")
        else:
            st.write(f"A volatilidade utilizada (sigma) foi definida pelo usuário: {sigma}")
        st.write(data.tail())  # Exibindo as últimas linhas dos dados simulados

