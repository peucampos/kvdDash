import streamlit as st
import locale
import pandas as pd
from datetime import datetime, timedelta
from home import authenticate_user

page_name = "Recuperação"

# Page configuration
st.set_page_config(page_title=page_name, page_icon="🔄", layout="wide")

# Verifica se o usuário está autenticado
if not authenticate_user():
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

# Set locale to Brazilian Portuguese
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


# Sidebar title
st.sidebar.title(page_name)  # Change the sidebar title

# Default date values
today = datetime.today()
one_month_ago = today - timedelta(days=30)

# Date filters in the sidebar
start_date = st.sidebar.date_input("Data Inicial", one_month_ago)
end_date = st.sidebar.date_input("Data Final", today)

# Ensure the end date is always set to 23:59:59
end_date = pd.to_datetime(end_date) + pd.Timedelta(hours=23, minutes=59, seconds=59)

st.title(page_name)

# Assuming df is the DataFrame resulting from your SQL query
# Connecting to the database and obtaining the data
conn = st.connection("my_database")
df = conn.query(f"""
SELECT u.cpf, u.name, u.phone, u.email, up.valid_until FROM user_plans up
JOIN users u ON u.id = up.user_id
WHERE up.valid_until BETWEEN '{start_date}' AND '{end_date}'
AND up.valid_until < '{today}'
AND u.deleted_at IS NULL
AND cpf IS NOT NULL
AND email IS NOT NULL
ORDER BY up.valid_until desc
""")

st.dataframe(df)
