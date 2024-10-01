import streamlit as st
import plotly.express as px
from home import authenticate_user
from datetime import datetime
import pandas as pd

page_name = "Afiliados"

# Configuração da página
st.set_page_config(page_title=page_name, page_icon="🧑‍💼", layout="wide")

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
SELECT ai.invited_id, ui.name, ai.user_id id_afiliado, u.name afiliado, ai.commission, ai.created_at, ai.payed_at, ai.type, ai.price, ai.discount, uba.pix_type, uba.pix_key
FROM affiliate_invitations ai
JOIN users u ON u.id = ai.user_id
JOIN users ui ON ui.id = ai.invited_id
LEFT JOIN user_bank_accounts uba ON uba.user_id = u.id
WHERE ai.payed_at IS NOT NULL AND ai.deleted_at IS NULL
AND ai.price IS NOT NULL AND ai.type IS NOT NULL
AND canceled_at IS NULL AND ai.chargebacked_at IS null
ORDER BY 1 DESC
""")

# Sidebar filter for start date and end date
st.sidebar.header("Filtrar por Data")
start_date = st.sidebar.date_input("Data Inicial", datetime.now() - pd.Timedelta(days=30))
end_date = st.sidebar.date_input("Data Final", datetime.now())

# Ensure the end date is always set to 23:59:59
end_date = pd.to_datetime(end_date) + pd.Timedelta(hours=23, minutes=59, seconds=59)

# Filter the dataframe based on the selected start date and end date
df = df[(df['payed_at'] >= pd.to_datetime(start_date)) & (df['payed_at'] <= pd.to_datetime(end_date))]

# Show metrics for total sale and total commission side by side
total_sale = df['price'].sum()
total_commission = df['commission'].sum()

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Vendas", f"R$ {total_sale:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
with col2:
    st.metric("Total Comissão", f"R$ {total_commission:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

# Pie charts side by side
st.header("Vendas por Tipo e Quantidade de Preços")

col1, col2 = st.columns(2)

with col1:
    # Pie chart for number of sales by type using Plotly
    sales_by_type = df['type'].value_counts().reset_index()
    sales_by_type.columns = ['type', 'count']

    # Replace 'family' with 'família' in the 'type' column
    sales_by_type['type'] = sales_by_type['type'].replace('family', 'família')

    fig = px.pie(sales_by_type, values='count', names='type', title='Vendas por Tipo', 
                 labels={'type': 'Tipo', 'count': 'Contagem'}, 
                 hole=0.3)

    st.plotly_chart(fig)

with col2:
    # Pie chart with quantity of prices
    prices = df['price'].value_counts().reset_index()
    prices.columns = ['price', 'count']

    fig_prices = px.pie(prices, values='count', names='price', title='Repetição de Preços', 
                        labels={'price': 'Preço', 'count': 'Contagem'}, 
                        hole=0.3)

    # Update the hoverinfo to show the count instead of the percentage
    fig_prices.update_traces(textinfo='label+value')

    st.plotly_chart(fig_prices)


# Bar chart for the total price by user
st.header("Vendas por Afiliado")

# Group by 'afiliado' and calculate the sum of 'price'
grouped_df = df.groupby('afiliado').agg({'price': 'sum'}).reset_index()

# Sort by 'price' in descending order and select the top 10
top_sellers = grouped_df.sort_values(by='price', ascending=False).head(10)

# Bar chart for the top 10 sellers with vertical bars
fig = px.bar(top_sellers, x='afiliado', y='price', title='Top 10 Vendedores',
                labels={'price': 'Valor', 'afiliado': 'Afiliado'})

# Show the values at the top of the bars
fig.update_traces(texttemplate='%{y:.2f}', textposition='outside')

# Increase the height of the figure
fig.update_layout(height=600)

st.plotly_chart(fig)

# Line chart for sales by day
st.header("Vendas por Dia")

# Group by 'payed_at' and calculate the sum of 'price'
df['payed_at'] = pd.to_datetime(df['payed_at']).dt.date
sales_by_day = df.groupby('payed_at')['price'].sum().reset_index()

# Line chart for sales by day using Plotly
fig_line = px.line(sales_by_day, x='payed_at', y='price', title='Vendas por Dia',
                   labels={'payed_at': 'Data', 'price': 'Valor'})

st.plotly_chart(fig_line)

# Checkbox for showing raw data grouped by users
if st.checkbox("Mostrar Dados Agrupados por Afiliados"):
    # Group by user_id and show the sum of price and commission
    grouped_df = df.groupby('id_afiliado').agg({
        'price': 'sum', 
        'commission': 'sum',
        'type': lambda x: (x == 'individual').sum(),  # Count of individual sales
        'discount': lambda x: (x > 0).sum()  # Count of sales with discount
    }).reset_index()

    # Rename the columns after aggregation
    grouped_df.columns = ['id_afiliado', 'total_price', 'total_commission', 'individual_sales', 'discount_sales']

    # Calculate the count of 'família' type sales
    family_sales_count = df[df['type'] == 'family'].groupby('id_afiliado')['type'].count().reset_index()
    family_sales_count.columns = ['id_afiliado', 'family_sales']

    # Merge with the grouped_df to include family sales count
    grouped_df = grouped_df.merge(family_sales_count, on='id_afiliado', how='left').fillna(0)

    # Merge with the original dataframe to get the user name, pix_type, and pix_key
    grouped_df = grouped_df.merge(df[['id_afiliado', 'afiliado', 'pix_type', 'pix_key']].drop_duplicates(), on='id_afiliado')

    # Reorder the columns
    grouped_df = grouped_df[['id_afiliado', 'afiliado', 'total_price', 'total_commission', 'individual_sales', 'family_sales', 'discount_sales', 'pix_type', 'pix_key']]

    # Sort by 'total_price' in descending order
    grouped_df = grouped_df.sort_values(by='total_price', ascending=False)

    st.write(grouped_df)


# Checkbox for showing raw data
if st.checkbox("Mostrar Dados"):
    
    # Selectbox for filtering by affiliate name
    affiliate_names = sorted(df['afiliado'].unique())
    selected_affiliate = st.selectbox("Selecione um Afiliado", options=["Todos"] + list(affiliate_names))

    # Filter the dataframe based on the selected affiliate
    if selected_affiliate != "Todos":        
        df = df[df['afiliado'] == selected_affiliate]

    st.write(df)

    # Display totalizers for commission, price, discount, and total sales (quantity)
    total_commission = df['commission'].sum()
    total_price = df['price'].sum()
    discount_sales_count = df[df['discount'] > 0].shape[0]
    total_sales_count = df.shape[0]
    family_sales_count = df[df['type'] == 'family'].shape[0]
    individual_sales_count = df[df['type'] == 'individual'].shape[0]

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Total Comissão:** R$ {total_commission:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.write(f"**Total Preço:** R$ {total_price:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.write(f"**Vendas com Desconto:** {discount_sales_count}")
    
    with col2:
        st.write(f"**Vendas Tipo Família:** {family_sales_count}")
        st.write(f"**Vendas Tipo Individual:** {individual_sales_count}")
        st.write(f"**Total de Vendas:** {total_sales_count}")
