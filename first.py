import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Conectando ao banco de dados
conn = st.connection("my_database")
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
    st.session_state.filter = 'Elegíveis'

# Exibir Total de Inelegíveis como métrica
col3.metric("Total de Inelegíveis", inelegiveis.shape[0])
if col3.button("Filtrar Total de Inelegíveis"):
    st.session_state.filter = 'Inelegíveis'

# Filtrar DataFrame com base na seleção do botão
if st.session_state.filter == 'Elegíveis':
    filtered_df = elegiveis
elif st.session_state.filter == 'Inelegíveis':
    filtered_df = inelegiveis
else:
    filtered_df = df  # Todos os usuários

# Exibir a tabela de dados se o checkbox estiver marcado
if st.checkbox('Mostrar dados'):
    st.dataframe(filtered_df)

# ----- Gráfico de Gênero -----

# Renomeando os gêneros para melhor visualização
filtered_df['gender'] = filtered_df['gender'].fillna('Não Definido')

filtered_df['gender'] = filtered_df['gender'].replace({
    'M': 'Homens',
    'F': 'Mulheres',
})

# Contar os gêneros, incluindo valores ausentes
gender_counts = filtered_df['gender'].value_counts()

# Criar gráfico de pizza usando Plotly
fig = px.pie(
    values=gender_counts.values, 
    names=gender_counts.index, 
    title="Distribuição de Gênero",
    color_discrete_sequence=['#66B2FF', '#FF9999', '#99FF99']  # Azul para Homens, Vermelho para Mulheres, Verde para Não Definido
)

# Customizar o texto para mostrar tanto percentual quanto quantidade
fig.update_traces(textposition='inside', textinfo='percent+label', 
                  texttemplate='%{label}<br>%{percent:.1%}<br>Qtd: %{value}')

# ----- Gráfico de Faixas Etárias -----

# Calcular a idade dos usuários
current_year = datetime.now().year
filtered_df['birthdate'] = pd.to_datetime(filtered_df['birthdate'], errors='coerce')  # Converter para datetime, ignorando erros
filtered_df['age'] = current_year - filtered_df['birthdate'].dt.year

# Remover idades inválidas (casos onde a data de nascimento era nula ou não pôde ser convertida)
filtered_df = filtered_df.dropna(subset=['age'])

# Categorizar em faixas etárias
bins = [0, 17, 27, 45, 59, 80, float('inf')]
labels = ['0-17', '18-27', '28-45', '46-59', '60-80', '80+']
filtered_df['faixa_etaria'] = pd.cut(filtered_df['age'], bins=bins, labels=labels, right=True)

# Contagem por faixa etária
faixa_etaria_counts = filtered_df['faixa_etaria'].value_counts().sort_index()

# Criar gráfico de barras usando Plotly
fig_age = px.bar(
    faixa_etaria_counts, 
    x=faixa_etaria_counts.index, 
    y=faixa_etaria_counts.values, 
    labels={'x': 'Faixa Etária', 'y': 'Quantidade'},
    title="Distribuição de Usuários por Faixa Etária",
    text=faixa_etaria_counts.values,  # Adicionar rótulos com os valores
    color_discrete_sequence=['#66B2FF']  # Definir a cor das barras
)

# Customizar o layout para melhor visualização
fig_age.update_traces(textposition='outside')
fig_age.update_layout(xaxis_title='Faixa Etária', yaxis_title='Quantidade de Usuários')

# ----- Exibir Gráficos Lado a Lado -----
col1, col2 = st.columns(2)  # Criar 2 colunas

# Exibir o gráfico de gênero na primeira coluna
with col1:
    st.plotly_chart(fig)

# Exibir o gráfico de faixa etária na segunda coluna
with col2:
    st.plotly_chart(fig_age)
