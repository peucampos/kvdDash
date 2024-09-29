import streamlit as st
import locale
from datetime import datetime, timedelta

# Set locale to Brazilian Portuguese
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

page_name = "Recuperação"

# Page configuration
st.set_page_config(page_title=page_name, page_icon="🔄", layout="wide")

# Sidebar title
st.sidebar.title(page_name)  # Change the sidebar title

# Default date values
today = datetime.today()
one_month_ago = today - timedelta(days=30)

# Date filters in the sidebar
start_date = st.sidebar.date_input("Data Inicial", one_month_ago)
end_date = st.sidebar.date_input("Data Final", today)

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