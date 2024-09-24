import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Conectando ao banco de dados
conn = st.connection("my_database_2")
df = conn.query("SELECT DISTINCT u.gender, u.birthdate, ua.estado, ua.cidade, ua.bairro, up.valid_until "
                "FROM users u "
                "LEFT JOIN user_addresses ua ON ua.user_id = u.id "
                "LEFT JOIN user_plans up ON up.user_id = u.id")

# Converter 'valid_until' para formato de data
df['valid_until'] = pd.to_datetime(df['valid_until'], errors='coerce')
today = pd.to_datetime(datetime.now().date())

# Calcular as métricas
total_users = df.shape[0]
elegiveis = df[df['valid_until'] >= today]
inelegiveis = df[df['valid_until'] < today]

# Inicializar o estado da sessão para o filtro
if 'filter' not in st.session_state:
    st.session_state.filter = 'Todos'  # Valor padrão

# Exibir as métricas
col1, col2, col3 = st.columns(3)

# Exibir Total de Usuários como métrica
col1.metric("Total de Usuários", total_users)
if col1.button("Filtrar Total de Usuários"):
    st.session_state.filter = 'Todos'

# Exibir Total de Elegíveis como métrica
col2.metric("Total de Elegíveis", elegiveis.shape[0])
if col2.button("Filtrar Total de Elegíveis"):
    st.s