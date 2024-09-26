import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

page_name = "Agendamentos"

# Configuração da página
st.set_page_config(page_title=page_name, page_icon="📅", layout="wide")

# Título da barra lateral
st.sidebar.title(page_name)  # Muda o título da sidebar

st.title(page_name)

# Connecting to the database and obtaining the data
conn = st.connection("my_database")
df = conn.query("""
SELECT ues.scheduled AS data_agendamento, u.id AS user_id, u.name AS user_name, u.gender, p.name AS provider, 
pu.name AS provider_unit, pu.bairro, ues.categoria, uess.status, ues.realizador_nome AS profissional, 
ues.procedimento_especialidade_nome
FROM user_exam_schedules ues
JOIN providers p ON p.id = ues.provider_id
JOIN provider_units pu ON pu.id = ues.provider_unit_id
JOIN users u ON u.id = ues.user_id
JOIN user_exam_schedule_statuses uess ON uess.id = ues.status_id
ORDER BY 1 DESC
""")

# Sidebar checkboxes for filtering categories
st.sidebar.header("Categoria")
show_consulta = st.sidebar.checkbox("Consulta", value=True)
show_exame = st.sidebar.checkbox("Imagem", value=True)
show_laboratorio = st.sidebar.checkbox("Laboratório", value=True)

# Sidebar checkboxes for filtering statuses
st.sidebar.header("Status")
show_agendado = st.sidebar.checkbox("Agendado", value=True)
show_cancelado = st.sidebar.checkbox("Cancelado", value=False)

# Sidebar checkboxes for filtering gender
st.sidebar.header("Gênero")
show_masculino = st.sidebar.checkbox("Masculino", value=True)
show_feminino = st.sidebar.checkbox("Feminino", value=True)

# Sidebar date input for filtering date range
st.sidebar.header("Data de Agendamento")
df['data_agendamento'] = pd.to_datetime(df['data_agendamento'])

# Default date range: from 12 months ago to today
default_start_date = datetime.today() - timedelta(days=365)
default_end_date = datetime.today()

start_date = st.sidebar.date_input("Data Inicial", value=default_start_date)
end_date = st.sidebar.date_input("Data Final", value=default_end_date)

# Format the dates to day/month/year
start_date = start_date.strftime('%d/%m/%Y')
end_date = end_date.strftime('%d/%m/%Y')

# Map gender values
gender_mapping = {
    'M': 'Masculino',
    'F': 'Feminino'
}
df['gender'] = df['gender'].map(gender_mapping)

# Apply filters based on the checkboxes and status
selected_status = []
if show_agendado:
    selected_status.append('Agendado')
if show_cancelado:
    selected_status.append('Cancelado')

# Apply filters based on the checkboxes, category, gender, and date range
filtered_df = df[
    (((df['categoria'] == 'L') & show_laboratorio) |
    ((df['categoria'] == 'C') & show_consulta) |
    ((df['categoria'] == 'E') & show_exame)) &
    (df['status'].isin(selected_status)) &
    (df['data_agendamento'] >= pd.to_datetime(start_date, format='%d/%m/%Y')) &
    (df['data_agendamento'] <= pd.to_datetime(end_date, format='%d/%m/%Y')) &
    (((df['gender'] == 'Masculino') & show_masculino) |
    ((df['gender'] == 'Feminino') & show_feminino))
]

# Mapping category codes to names
category_mapping = {
    'L': 'Laboratório',
    'C': 'Consulta',
    'E': 'Imagem'
}

# Metrics showing the total number of schedules and the number of schedules by status
total_schedules = filtered_df.shape[0]
total_schedules_by_status = filtered_df['status'].value_counts()

# Display metrics side by side
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total de Agendamentos", total_schedules)
with col2:
    st.metric("Agendados", total_schedules_by_status.get('Agendado', 0))
with col3:
    st.metric("Cancelados", total_schedules_by_status.get('Cancelado', 0))

# Replace category codes with names
filtered_df['categoria'] = filtered_df['categoria'].map(category_mapping)

# Schedules by category and status side by side
col1, col2 = st.columns(2)

with col1:
    fig = px.pie(filtered_df, names='categoria', title='Agendamentos por Categoria')
    st.plotly_chart(fig)

with col2:
    fig = px.pie(filtered_df, names='status', title='Agendamentos por Status')
    st.plotly_chart(fig)

# Schedule by specialty
specialty_counts = filtered_df['procedimento_especialidade_nome'].value_counts().reset_index()
specialty_counts.columns = ['Especialidade', 'Quantidade']
fig = px.histogram(specialty_counts, x='Especialidade', y='Quantidade', title='Agendamentos por Especialidade',
                   category_orders={'Especialidade': specialty_counts['Especialidade'].tolist()})
st.plotly_chart(fig)

# Schedules by provider
provider_counts = filtered_df['provider'].value_counts().reset_index()
provider_counts.columns = ['Credenciado', 'Quantidade']

fig = px.histogram(provider_counts, x='Credenciado', y='Quantidade', title='Agendamentos por Credenciado', 
                   category_orders={'Credenciado': provider_counts['Credenciado'].tolist()})
st.plotly_chart(fig)

# Schedule by provider unit
filtered_df['unidade_bairro'] = filtered_df['provider_unit'] + " - " + filtered_df['bairro']
provider_unit_counts = filtered_df['unidade_bairro'].value_counts().reset_index()
provider_unit_counts.columns = ['Unidade - Bairro', 'Quantidade']
fig = px.histogram(provider_unit_counts, x='Unidade - Bairro', y='Quantidade', title='Agendamentos por Unidade',
                   category_orders={'Unidade - Bairro': provider_unit_counts['Unidade - Bairro'].tolist()})
st.plotly_chart(fig)

# Schedules by date and status
fig = px.histogram(filtered_df, x='data_agendamento', color='status', title='Agendamentos por Data e Status')
st.plotly_chart(fig)

# Schedules by professionals (only top 20)
professional_counts = filtered_df['profissional'].value_counts().reset_index().head(20)
professional_counts.columns = ['Profissional', 'Quantidade']
fig = px.histogram(professional_counts, x='Profissional', y='Quantidade', title='Top 20 Agendamentos por Profissional',
                   category_orders={'Profissional': professional_counts['Profissional'].tolist()})
st.plotly_chart(fig)

# Display the data table if checkbox is checked
if st.checkbox("Mostrar Dados"):
    st.dataframe(filtered_df)