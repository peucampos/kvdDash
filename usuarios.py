import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="Usuários",  # Título que aparecerá na aba do navegador
    page_icon="👤",  # Ícone que aparecerá na aba do navegador
    layout="wide"  # Layout da página (pode ser "wide" ou "centered")
)

# Título da barra lateral
st.sidebar.title("Usuários")  # Muda o título da sidebar

st.title("Usuários")

# Conectando ao banco de dados
conn = st.connection("my_database")
df = conn.query("SELECT DISTINCT u.id, u.name, u.email, u.phone, u.gender, u.birthdate, ua.estado, " 
                "ua.cidade, ua.bairro, up.valid_until, uf.permission, uhp.weight, uhp.height "
                "FROM users u "
                "LEFT JOIN user_addresses ua ON ua.user_id = u.id "
                "LEFT JOIN user_plans up ON up.user_id = u.id "
                "LEFT JOIN user_families uf ON uf.user_id = u.id "
                "LEFT JOIN user_health_profiles uhp ON uhp.user_id = u.id")

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
filtered_df['gender'] = filtered_df['gender'].fillna('Não Definido').replace({'M': 'Homens', 'F': 'Mulheres'})
gender_counts = filtered_df['gender'].value_counts()
fig = px.pie(values=gender_counts.values, names=gender_counts.index, title="Distribuição de Gênero", color_discrete_sequence=['#66B2FF', '#FF9999', '#99FF99'])
fig.update_traces(textposition='inside', textinfo='percent+label', texttemplate='%{label}<br>%{percent:.1%}<br>Qtd: %{value}')

# ----- Gráfico de Faixas Etárias -----
current_year = datetime.now().year
filtered_df['birthdate'] = pd.to_datetime(filtered_df['birthdate'], errors='coerce')
filtered_df['age'] = current_year - filtered_df['birthdate'].dt.year
filtered_df = filtered_df.dropna(subset=['age'])
bins = [0, 17, 27, 45, 59, 80, float('inf')]
labels = ['0-17', '18-27', '28-45', '46-59', '60-80', '80+']
filtered_df['faixa_etaria'] = pd.cut(filtered_df['age'], bins=bins, labels=labels, right=True)
faixa_etaria_counts = filtered_df['faixa_etaria'].value_counts().sort_index()
fig_age = px.bar(faixa_etaria_counts, x=faixa_etaria_counts.index, y=faixa_etaria_counts.values, labels={'x': 'Faixa Etária', 'y': 'Quantidade'}, title="Distribuição de Usuários por Faixa Etária", text=faixa_etaria_counts.values, color_discrete_sequence=['#66B2FF'])
fig_age.update_traces(textposition='outside')
fig_age.update_layout(xaxis_title='Faixa Etária', yaxis_title='Quantidade de Usuários')

# ----- Gráfico de Tipo de Passaporte -----
filtered_df['permission'] = filtered_df['permission'].fillna('Familiar')
filtered_df['permission'] = filtered_df['permission'].apply(lambda x: 'Titular' if x == 'family-owner' else 'Familiar')
permission_counts = filtered_df['permission'].value_counts()
fig_permission = px.pie(values=permission_counts.values, names=permission_counts.index, title="Distribuição por Tipo de Passaporte", color_discrete_sequence=['#FF9999', '#66B2FF'])
fig_permission.update_traces(textposition='inside', textinfo='percent+label', texttemplate='%{label}<br>%{percent:.1%}<br>Qtd: %{value}')

# ----- Gráfico de Quantidade de Usuários por Bairro -----

# Contagem de usuários por bairro
bairro_counts = filtered_df['bairro'].value_counts().nlargest(100)  # Selecionar os 20 bairros com mais usuários

# Criar gráfico de barras horizontais usando Plotly
fig_bairro = px.bar(
    bairro_counts,
    x=bairro_counts.values,
    y=bairro_counts.index,
    labels={'x': 'Quantidade de Usuários', 'y': 'Bairro'},
    title="Top 10 Bairros por Quantidade de Usuários",
    text=bairro_counts.values,  # Adicionar rótulos com os valores
    orientation='h',  # Barras horizontais
    color_discrete_sequence=['#66B2FF']  # Cor das barras
)

# Customizar o layout para mostrar apenas 10 registros por vez
fig_bairro.update_layout(
    height=640,  # Altura do gráfico
    yaxis_range=[-1, 10],  # Mostrar apenas 10 registros por vez
)

# Customizar o layout para melhor visualização
fig_bairro.update_traces(textposition='outside')
fig_bairro.update_layout(xaxis_title='Quantidade de Usuários', yaxis_title='Bairro')
fig_bairro.update_yaxes(categoryorder='total descending')  # Ordenar por quantidade de usuários (maior para menor)

# Mover o eixo x para o topo
fig_bairro.update_xaxes(side='top')

# ----- Gráfico de Níveis de Obesidade -----
filtered_df['BMI'] = filtered_df['weight'] / (filtered_df['height'] ** 2)
filtered_df = filtered_df[(filtered_df['BMI'].notnull()) & (filtered_df['weight'] <= 200)]
obesity_bins = [0, 18.5, 24.9, 29.9, 34.9, 39.9, float('inf')]
obesity_labels = ['Abaixo do Peso', 'Peso Normal', 'Sobrepeso', 'Obesidade Grau 1', 'Obesidade Grau 2', 'Obesidade Grau 3']
filtered_df['obesity_level'] = pd.cut(filtered_df['BMI'], bins=obesity_bins, labels=obesity_labels)
obesity_counts = filtered_df['obesity_level'].value_counts().sort_index()
fig_obesity = px.bar(obesity_counts, x=obesity_counts.index, y=obesity_counts.values, labels={'x': 'Nível de Obesidade', 'y': 'Quantidade'}, title="Distribuição de Níveis de Obesidade", text=obesity_counts.values, color_discrete_sequence=['#FF9999'])
fig_obesity.update_traces(textposition='outside')
fig_obesity.update_layout(xaxis_title='Nível de Obesidade', yaxis_title='Quantidade de Usuários')


# ----- Exibir Gráficos Lado a Lado -----
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig)
with col2:
    st.plotly_chart(fig_age)
st.plotly_chart(fig_obesity)
st.plotly_chart(fig_permission)
st.plotly_chart(fig_bairro)
