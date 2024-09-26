import streamlit as st

page_name = "Passaportes"

# Configuração da página
st.set_page_config(page_title=page_name, page_icon="🛂", layout="wide")

# Título da barra lateral
st.sidebar.title(page_name)  # Muda o título da sidebar

st.title(page_name)