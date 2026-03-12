import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="Dashboard Evolução Mensal", layout="wide")
st.title("Evolução Mensal de Vendas (Ano Completo)")

# ==========================================
# 2. LEITURA E TRATAMENTO DOS DADOS
# ==========================================
try:
    df_fat = pd.read_csv('faturamento2025.csv')
    df_prod = pd.read_csv('produto2025.csv')
except FileNotFoundError:
    st.error("Arquivos CSV não encontrados na pasta. Verifique os nomes exatos!")
    st.stop()

# --- LIMPEZA DE FATURAMENTO ---
# Remover as linhas de Total Geral (que não têm o mês preenchido e sujam a matemática)
df_fat = df_fat.dropna(subset=['MES'])
df_fat = df_fat[~df_fat['CLIENTE'].astype(str).str.contains("TOTAL GERAL", na=False)]

# Converter as colunas para números
df_fat['MES'] = pd.to_numeric(df_fat['MES'], errors='coerce').fillna(0).astype(int)
if 'VALOR_FATURADO' in df_fat.columns:
    df_fat['VALOR_FATURADO'] = pd.to_numeric(df_fat['VALOR_FATURADO'], errors='coerce').fillna(0)

# --- LIMPEZA DE PRODUTOS ---
df_prod = df_prod.dropna(subset=['MES'])
df_prod['MES'] = pd.to_numeric(df_prod['MES'], errors='coerce').fillna(0).astype(int)

for col in ['Qtd Total', 'Valor Total']:
    if col in df_prod.columns:
        df_prod[col] = pd.to_numeric(df_prod[col], errors='coerce').fillna(0)

if 'COD_PRODUTO' in df_prod.columns:
    df_prod['COD_PRODUTO'] = df_prod['COD_PRODUTO'].fillna("").astype(str)
    df_prod['COD_PRODUTO'] = df_prod['COD_PRODUTO'].apply(lambda x: x.replace('.0', '') if x.endswith('.0') else x)

if 'NOME_PRODUTO' in df_prod.columns:
    df_prod['NOME_PRODUTO'] = df_prod['NOME_PRODUTO'].fillna("").astype(str)

# Traduzir o número do mês para nome para ficar visualmente profissional
meses_pt = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun', 
            7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}

df_fat['NOME_MES'] = df_fat['MES'].map(meses_pt)
df_prod['NOME_MES'] = df_prod['MES'].map(meses_pt)

# ==========================================
# 3. CÁLCULO DE MÉTRICAS GERAIS
# ==========================================
faturamento_total = df_fat['VALOR_FATURADO'].sum() if 'VALOR_FATURADO' in df_fat.columns else 0

st.info("Insight Baseado em Dados: A curva abaixo demonstra a evolução do faturamento ao longo dos meses do ano.")

# Métrica em Destaque
st.metric("Faturamento Total Acumulado (Ano)", f"R$ {faturamento_total:,.2f}")

st.markdown("---")

# ==========================================
# 4. GRÁFICOS INTERATIVOS
# ==========================================
col_grafico1, col_grafico2 = st.columns(2)

with col_grafico1:
    st.subheader("Curva de Faturamento Mensal")
    
    # Agrupar faturamento mês a mês e garantir ordem cronológica correta
    df_mes = df_fat.groupby(['MES', 'NOME_MES'])['VALOR_FATURADO'].sum().reset_index()
    df_mes = df_mes.sort_values('MES')
    
    # Criar um texto formatado em R$ para os pontos do gráfico
    df_mes['TEXTO_VALOR'] = df_mes['VALOR_FATURADO'].apply(lambda x: f"R$ {x:,.2f}")
    
    fig1 = px.line(
        df_mes, x='NOME_MES', y='VALOR_FATURADO', markers=True, text='TEXTO_VALOR',
        labels={'NOME_MES': 'Mês', 'VALOR_FATURADO': 'Faturamento (R$)'},
        template="plotly_white"
    )
    fig1.update_traces(line_color='#2980b9', line_width=4, marker_size=10, textposition='top center')
    # Forçar o eixo Y a começar em zero para a proporção ficar correta
    fig1.update_yaxes(rangemode="tozero")
    st.plotly_chart(fig1, use_container_width=True)

with col_grafico2:
    st.subheader("Top Produtos no Ano (Valor)")
    
    df_top_prod = df_prod.groupby('NOME_PRODUTO')['Valor Total'].sum().nlargest(10).reset_index()
    
    fig2 = px.bar(
        df_top_prod, x='Valor Total', y='NOME_PRODUTO', orientation='h',
        labels={'NOME_PRODUTO': '', 'Valor Total': 'Faturamento (R$)'},
        template="plotly_white"
    )
    # Inverter o eixo Y para o maior ficar no topo
    fig2.update_layout(yaxis={'categoryorder':'total ascending'})
    fig2.update_traces(marker_color='#27ae60')
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ==========================================
# 5. TABELAS DE DADOS 
# ==========================================
st.subheader("Detalhamento Base de Dados")

tab1, tab2 = st.tabs(["Faturamento por Mês", "Detalhamento de Produtos"])

with tab1:
    st.dataframe(
        df_fat.style.format({
            "VALOR_FATURADO": "R$ {:,.2f}"
        }),
        use_container_width=True, height=400
    )

with tab2:
    st.dataframe(
        df_prod.style.format({
            "Qtd Total": "{:,.2f}", 
            "Valor Total": "R$ {:,.2f}"
        }),
        use_container_width=True, height=500
    )