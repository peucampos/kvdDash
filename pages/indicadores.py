import streamlit as st
import plotly.express as px
from home import authenticate_user
from datetime import datetime
import pandas as pd

page_name = "Indicadores"

# Configuração da página
st.set_page_config(page_title=page_name, page_icon="📊", layout="wide")

# Verifica se o usuário está autenticado
if not authenticate_user():
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

# Título da barra lateral
st.sidebar.title(page_name)  # Muda o título da sidebar

st.title(page_name)

# Connecting to the database and obtaining the data
conn = st.connection("my_database")
df = conn.query("""
SELECT distinct u.id, u.name, u.birthdate, u.gender, u.email, u.phone, 
a.name alergia, cd.name cronicas, sc.name condicoes, uhp.weight, uhp.height,
(uhp.weight / (uhp.height * uhp.height)) imc, bt.name sangue, uhp.restrictions
FROM users u
LEFT JOIN user_allergies ua ON ua.user_id = u.id
LEFT JOIN allergies a ON a.id = ua.allergy_id
LEFT JOIN user_chronic_diseases ucd ON ucd.user_id = u.id
LEFT JOIN chronic_diseases cd ON cd.id = ucd.user_id
LEFT JOIN user_special_conditions usc ON usc.user_id = u.id
LEFT JOIN special_conditions sc ON sc.id = usc.special_condition_id
LEFT JOIN user_health_profiles uhp ON uhp.user_id = u.id
LEFT JOIN blood_types bt ON bt.id = uhp.blood_type_id
""")

# Create filters for the user data
st.sidebar.subheader("Filtros")

# Filter for allergies
allergy_options = df['alergia'].dropna().unique()
selected_allergies = st.sidebar.multiselect('Alergias', allergy_options)

# Filter for chronic diseases
chronic_disease_options = df['cronicas'].dropna().unique()
selected_chronic_diseases = st.sidebar.multiselect('Doenças Crônicas', chronic_disease_options)

# Filter for special conditions
special_condition_options = df['condicoes'].dropna().unique()
selected_special_conditions = st.sidebar.multiselect('Condições Especiais', special_condition_options)

# Filter for age range
df['birthdate'] = pd.to_datetime(df['birthdate'], errors='coerce')
df = df.dropna(subset=['birthdate'])
df['age'] = (datetime.now() - df['birthdate']).dt.days // 365
age_bins = [0, 18, 30, 40, 50, 60, 70, 80, 90, 100]
age_labels = ['0-18', '19-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90', '91-100']
df['age_range'] = pd.cut(df['age'], bins=age_bins, labels=age_labels)
age_range_options = df['age_range'].dropna().unique()
selected_age_ranges = st.sidebar.multiselect('Faixa Etária', age_range_options)

# Filter for gender
gender_options = df['gender'].dropna().unique()
selected_genders = st.sidebar.multiselect('Gênero', gender_options)

# Filter for blood type
blood_type_options = df['sangue'].dropna().unique()
selected_blood_types = st.sidebar.multiselect('Tipo Sanguíneo', blood_type_options)

# Filter for IMC
imc_bins = [0, 18.5, 24.9, 29.9, 34.9, 39.9, float('inf')]
imc_labels = ['Abaixo do Peso', 'Peso Normal', 'Sobrepeso', 'Obesidade Grau I', 'Obesidade Grau II', 'Obesidade Grau III']
df['imc_range'] = pd.cut(df['imc'], bins=imc_bins, labels=imc_labels)
imc_range_options = df['imc_range'].dropna().unique()
selected_imc_ranges = st.sidebar.multiselect('Faixa de IMC', imc_range_options)

# Apply filters to the dataframe
if selected_allergies:
    df = df[df['alergia'].isin(selected_allergies)]
if selected_chronic_diseases:
    df = df[df['cronicas'].isin(selected_chronic_diseases)]
if selected_special_conditions:
    df = df[df['condicoes'].isin(selected_special_conditions)]
if selected_age_ranges:
    df = df[df['age_range'].isin(selected_age_ranges)]
if selected_genders:
    df = df[df['gender'].isin(selected_genders)]
if selected_blood_types:
    df = df[df['sangue'].isin(selected_blood_types)]
if selected_imc_ranges:
    df = df[df['imc_range'].isin(selected_imc_ranges)]

# Pie charts for allergies, chronic diseases, and special conditions side by side
st.header("Alergias, Doenças Crônicas e Condições Especiais")
col1, col2, col3 = st.columns(3)

# Pie chart for allergies
allergies = df['alergia'].value_counts().reset_index()
allergies.columns = ['alergia', 'count']
fig = px.pie(allergies, values='count', names='alergia', title='Alergias')
col1.plotly_chart(fig)

# Pie chart for chronic diseases
chronic_diseases = df['cronicas'].value_counts().reset_index()
chronic_diseases.columns = ['cronicas', 'count']
fig = px.pie(chronic_diseases, values='count', names='cronicas', title='Doenças Crônicas')
col2.plotly_chart(fig)

# Pie chart for special conditions
special_conditions = df['condicoes'].value_counts().reset_index()
special_conditions.columns = ['condicoes', 'count']
fig = px.pie(special_conditions, values='count', names='condicoes', title='Condições Especiais')
col3.plotly_chart(fig)

# Remove duplicate users based on user.id
df = df.drop_duplicates(subset=['id'])

# Pie charts for age range and gender distribution side by side
st.header("Faixa Etária e Distribuição de Gênero")
col1, col2 = st.columns(2)

# Pie chart for age range
age_range = df['age_range'].value_counts().reset_index()
age_range.columns = ['age_range', 'count']
fig = px.pie(age_range, values='count', names='age_range', title='Faixa Etária')
col1.plotly_chart(fig)

# Pie chart for gender distribution
gender_distribution = df['gender'].value_counts().reset_index()
gender_distribution.columns = ['gender', 'count']
fig = px.pie(gender_distribution, values='count', names='gender', title='Distribuição de Gênero')
col2.plotly_chart(fig)

# Pie charts for blood type and IMC range side by side
st.header("Tipo Sanguíneo e Faixa de IMC")
col1, col2 = st.columns(2)

# Pie chart for blood type
blood_type = df['sangue'].value_counts().reset_index()
blood_type.columns = ['sangue', 'count']
fig = px.pie(blood_type, values='count', names='sangue', title='Tipo Sanguíneo')
col1.plotly_chart(fig)

# Pie chart for IMC range
imc_distribution = df['imc_range'].value_counts().reset_index()
imc_distribution.columns = ['imc_range', 'count']
fig = px.pie(imc_distribution, values='count', names='imc_range', title='Faixa de IMC')
col2.plotly_chart(fig)

# Show the table with the user data
st.header("Dados dos Usuários")
st.write(df)