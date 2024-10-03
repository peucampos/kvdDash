import streamlit as st
import pandas as pd
import locale
import plotly.express as px
from home import authenticate_user

page_name = "Pagamentos"

# Page configuration
st.set_page_config(page_title=page_name, page_icon="💰", layout="wide")

# Verifica se o usuário está autenticado
if not authenticate_user():
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

# Set locale to Brazilian Portuguese
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Sidebar title
st.sidebar.title(page_name)  # Change the sidebar title

st.title(page_name)

# Assuming df is the DataFrame resulting from your SQL query
# Connecting to the database and obtaining the data
conn = st.connection("my_database")
df = conn.query("""
SELECT up.created_at, up.updated_at, u.id as user_id, u.name as user, ups.slug as STATUS, up.payable_type, 
up.pay_type, up.installments, up.price, up.split_value split, up.sell_affiliate, up.sell_app, up.sell_landpage, up.sell_klingo
FROM user_payments up
LEFT JOIN users u ON u.id = up.user_id
LEFT JOIN user_payment_statuses ups ON ups.id = up.user_payment_status_id
""")

# Mapping statuses to categories
status_map = {
    'paid': 'Pago',
    'refunded': 'Cancelado',
    'chargedback': 'Cancelado',
    'canceled': 'Cancelado',
    'refused': 'Incompleto',
    'pending': 'Incompleto'
}
df['status_category'] = df['STATUS'].map(status_map).fillna('Incompleto')

# Sidebar checkboxes for filtering payment types
st.sidebar.header("Tipo de Pagamento")
show_passaporte = st.sidebar.checkbox("Passaporte", value=True)
show_agendamentos = st.sidebar.checkbox("Agendamentos", value=True)
show_split = st.sidebar.checkbox("Split", value=True)

# Sidebar checkboxes for filtering payment statuses
st.sidebar.header("Status")
show_paid = st.sidebar.checkbox("Pago", value=True)
show_canceled = st.sidebar.checkbox("Cancelado/Estornado", value=False)
show_incomplete = st.sidebar.checkbox("Incompleto", value=False)

# Apply filters based on the selected checkboxes for payment status
selected_status_categories = []
if show_paid:
    selected_status_categories.append('Pago')
if show_canceled:
    selected_status_categories.append('Cancelado')
if show_incomplete:
    selected_status_categories.append('Incompleto')

# Apply filters based on the selected checkboxes for payment types
selected_payment_types = []
if show_passaporte:
    selected_payment_types.append('plans')
if show_agendamentos:
    selected_payment_types.append('appointments')
if show_split:
    selected_payment_types.append('split')

# Filter the dataframe based on the selected checkboxes
filtered_df = df[
    df['status_category'].isin(selected_status_categories) &
    df['payable_type'].isin(selected_payment_types)
]

# Adjust price based on split selection
if not show_split:
    filtered_df['price'] = filtered_df['price'] - filtered_df['split']

# Calculating metrics based on the filter
paid_sum = filtered_df[filtered_df['status_category'] == 'Pago']['price'].sum()
canceled_sum = filtered_df[filtered_df['status_category'] == 'Cancelado']['price'].sum()
incomplete_sum = filtered_df[filtered_df['status_category'] == 'Incompleto']['price'].sum()
split_sum = filtered_df['split'].sum() if show_split else 0

# Displaying metrics side by side
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Pago", f"R$ {locale.format_string('%.2f', paid_sum, grouping=True)}")
col2.metric("Total Cancelado/Estornado", f"R$ {locale.format_string('%.2f', canceled_sum, grouping=True)}")
col3.metric("Total Incompleto", f"R$ {locale.format_string('%.2f', incomplete_sum, grouping=True)}")
col4.metric("Total Split", f"R$ {locale.format_string('%.2f', split_sum, grouping=True)}")

# Sidebar date input for filtering by date range
st.sidebar.header("Filtro por Data")
start_date = st.sidebar.date_input("Data Inicial", value=pd.Timestamp.today() - pd.DateOffset(months=12))
end_date = st.sidebar.date_input("Data Final", value=pd.Timestamp.today())

# Ensure the end date is always set to 23:59:59
end_date = pd.to_datetime(end_date) + pd.Timedelta(hours=23, minutes=59, seconds=59)

# Filter the dataframe based on the selected date range
filtered_df = filtered_df[(filtered_df['created_at'] >= pd.to_datetime(start_date)) & 
                          (filtered_df['created_at'] <= pd.to_datetime(end_date))]

# Show a line chart of the total amount by month considering all filters
st.header("Total por Mês")

# Convert 'created_at' to datetime and create 'year_month' column
filtered_df['created_at'] = pd.to_datetime(filtered_df['created_at'])
filtered_df['year_month'] = filtered_df['created_at'].dt.to_period('M')

# Group by year_month and sum the prices
monthly_total = filtered_df.groupby('year_month')['price'].sum()

# Convert PeriodIndex to string for better display
monthly_total.index = monthly_total.index.astype(str)

# Create two columns for the chart and the table with different widths
col1, col2 = st.columns([3, 1])  # Allocate more space to the first column

# Show the line chart in the first column
with col1:
    st.line_chart(monthly_total)

# Display the values in the line chart in the second column with formatted currency, ordered by date descending
with col2:
    formatted_monthly_total = monthly_total.apply(lambda x: f"{locale.format_string('%.2f', x, grouping=True)}")
    formatted_monthly_total = formatted_monthly_total.sort_index(ascending=False)
    st.write(formatted_monthly_total)

# Create pie charts for payment sources, payment types, and installments
st.header("Distribuição de Pagamentos")

# Create three columns for the pie charts
col1, col2, col3 = st.columns(3)

# Payment sources pie chart
with col1:
    st.subheader("Fontes de Pagamento")
    payment_sources = filtered_df[['sell_affiliate', 'sell_app', 'sell_landpage', 'sell_klingo']].sum()
    payment_sources = payment_sources.fillna('N/A')  # Replace NaN with 'N/A'
    fig1 = px.pie(values=payment_sources, names=payment_sources.index, title='Fontes de Pagamento')
    st.plotly_chart(fig1)

# Payment types pie chart
with col2:
    st.subheader("Formas de Pagamento")
    payment_types = filtered_df['pay_type'].fillna('N/A').value_counts()  # Replace NaN with 'N/A'
    fig2 = px.pie(values=payment_types, names=payment_types.index, title='Formas de Pagamento')
    st.plotly_chart(fig2)

# Installments pie chart
with col3:
    st.subheader("Número de Parcelas")
    installments = filtered_df['installments'].value_counts()  # Replace NaN with 'N/A'
    fig3 = px.pie(values=installments, names=installments.index, title='Número de Parcelas')
    st.plotly_chart(fig3)

if st.checkbox("Vendas por Hora"):
    st.header("Vendas por Hora")
    # Add slider for selecting hour range
    start_hour, end_hour = st.slider(
        "Selecione o intervalo de horas",
        min_value=0,
        max_value=23,
        value=(6, 18),
        format="%02d:00"
    )
    # Filter the dataframe based on the selected hour range
    filtered_df['hour'] = filtered_df['created_at'].dt.hour
    filtered_df = filtered_df[(filtered_df['hour'] >= start_hour) & (filtered_df['hour'] <= end_hour)]

    # Filter the dataframe based on the selected date range
    filtered_df = filtered_df[(filtered_df['created_at'] >= pd.to_datetime(start_date)) & 
                              (filtered_df['created_at'] <= pd.to_datetime(end_date))]

    # Group by date and sum the prices
    daily_total = filtered_df.groupby(filtered_df['created_at'].dt.date)['price'].sum()

    # Create a line chart for sales by day within the selected hour range
    fig = px.line(daily_total, x=daily_total.index, y='price', labels={'x': 'Data', 'price': 'Total de Vendas'}, title='Vendas por Dia dentro do Intervalo de Horas')
    st.plotly_chart(fig)

if st.checkbox("Vendas por Dia do Mês"):
    st.header("Vendas por Dia do Mês")
    # Add slider for selecting day range
    start_day, end_day = st.slider(
        "Selecione o intervalo de dias",
        min_value=1,
        max_value=31,
        value=(1, 31),
        format="%d"
    )
    # Filter the dataframe based on the selected day range
    filtered_df['day'] = filtered_df['created_at'].dt.day
    filtered_df = filtered_df[(filtered_df['day'] >= start_day) & (filtered_df['day'] <= end_day)]

    # Group by year_month and sum the prices
    monthly_total = filtered_df.groupby('year_month')['price'].sum()

    # Convert PeriodIndex to string for better display
    monthly_total.index = monthly_total.index.astype(str)

    # Create a line chart for sales by month within the selected day range
    fig = px.bar(monthly_total, x=monthly_total.index, y='price', labels={'x': 'Mês', 'price': 'Total de Vendas'}, title='Vendas por Mês dentro do Intervalo de Dias')
    st.plotly_chart(fig)


# Display the data table if checkbox is checked
if st.checkbox("Mostrar Dados"):
    st.dataframe(filtered_df)