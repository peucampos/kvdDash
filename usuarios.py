import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="Users",  # Title that will appear in the browser tab
    page_icon="👤",  # Icon that will appear in the browser tab
    layout="wide"  # Page layout (can be "wide" or "centered")
)

# Sidebar title
st.sidebar.title("Users")  # Change the sidebar title

st.title("Users")

# Connecting to the database
conn = st.connection("my_database")
df = conn.query("SELECT DISTINCT u.id, u.name, u.email, u.phone, u.gender, u.birthdate, ua.estado, "
                "ua.cidade, ua.bairro, up.valid_until, uf.permission, uhp.weight, uhp.height "
                "FROM users u "
                "LEFT JOIN user_addresses ua ON ua.user_id = u.id "
                "LEFT JOIN user_plans up ON up.user_id = u.id "
                "LEFT JOIN user_families uf ON uf.user_id = u.id "
                "LEFT JOIN user_health_profiles uhp ON uhp.user_id = u.id")

# Convert 'valid_until' to date format
df['valid_until'] = pd.to_datetime(df['valid_until'], errors='coerce')
today = pd.to_datetime(datetime.now().date())

# Filter DataFrame to include only rows where 'valid_until' is not null
df_filtered = df[df['valid_until'].notnull()]

# Add a filter to show all users, only eligible or only ineligible in the sidebar
st.sidebar.radio("Filter by Eligibility", ['All', 'Eligible', 'Ineligible'], key='filter')

# Calculate metrics
total_users = df_filtered.shape[0]
eligible = df_filtered[df_filtered['valid_until'] >= today]
ineligible = df_filtered[df_filtered['valid_until'] < today]

# Initialize session state for the filter
if 'filter' not in st.session_state:
    st.session_state.filter = 'All'  # Default value

# Display metrics
col1, col2, col3 = st.columns(3)

# Display Total Users as a metric
col1.metric("Total Users", total_users)

# Display Total Eligible as a metric
col2.metric("Total Eligible", eligible.shape[0])

# Display Total Ineligible as a metric
col3.metric("Total Ineligible", ineligible.shape[0])

# Filter DataFrame based on button selection
if st.session_state.filter == 'Eligible':
    filtered_df = eligible
elif st.session_state.filter == 'Ineligible':
    filtered_df = ineligible
else:
    filtered_df = df  # All users

# ----- Gender Chart -----
filtered_df['gender'] = filtered_df['gender'].fillna('Not Defined').replace({'M': 'Men', 'F': 'Women'})
gender_counts = filtered_df['gender'].value_counts()
fig = px.pie(values=gender_counts.values, names=gender_counts.index, title="Gender Distribution", color_discrete_sequence=['#66B2FF', '#FF9999', '#99FF99'])
fig.update_traces(textposition='inside', textinfo='percent+label', texttemplate='%{label}<br>%{percent:.1%}<br>Qty: %{value}')

# ----- Age Group Chart -----
current_year = datetime.now().year
filtered_df['birthdate'] = pd.to_datetime(filtered_df['birthdate'], errors='coerce')
filtered_df['age'] = current_year - filtered_df['birthdate'].dt.year
filtered_df = filtered_df.dropna(subset=['age'])
bins = [0, 17, 27, 45, 59, 80, float('inf')]
labels = ['0-17', '18-27', '28-45', '46-59', '60-80', '80+']
filtered_df['age_group'] = pd.cut(filtered_df['age'], bins=bins, labels=labels, right=True)
age_group_counts = filtered_df['age_group'].value_counts().sort_index()
fig_age = px.bar(age_group_counts, x=age_group_counts.index, y=age_group_counts.values, labels={'x': 'Age Group', 'y': 'Quantity'}, title="User Distribution by Age Group", text=age_group_counts.values, color_discrete_sequence=['#66B2FF'])
fig_age.update_traces(textposition='outside')
fig_age.update_layout(xaxis_title='Age Group', yaxis_title='Number of Users')

# ----- Passport Type Chart -----
filtered_df['permission'] = filtered_df['permission'].fillna('Family')
filtered_df['permission'] = filtered_df['permission'].apply(lambda x: 'Primary' if x == 'family-owner' else 'Family')
permission_counts = filtered_df['permission'].value_counts()
fig_permission = px.pie(values=permission_counts.values, names=permission_counts.index, title="Distribution by Passport Type", color_discrete_sequence=['#FF9999', '#66B2FF'])
fig_permission.update_traces(textposition='inside', textinfo='percent+label', texttemplate='%{label}<br>%{percent:.1%}<br>Qty: %{value}')

# ----- User Count by Neighborhood Chart -----

# User count by neighborhood
neighborhood_counts = filtered_df['bairro'].value_counts().nlargest(100)  # Select the top 20 neighborhoods with the most users

# Create horizontal bar chart using Plotly
fig_neighborhood = px.bar(
    neighborhood_counts,
    x=neighborhood_counts.values,
    y=neighborhood_counts.index,
    labels={'x': 'Number of Users', 'y': 'Neighborhood'},
    title="Top 10 Neighborhoods by Number of Users",
    text=neighborhood_counts.values,  # Add labels with values
    orientation='h',  # Horizontal bars
    color_discrete_sequence=['#66B2FF']  # Bar color
)

# Customize layout to show only 10 records at a time
fig_neighborhood.update_layout(
    height=640,  # Chart height
    yaxis_range=[-1, 10],  # Show only 10 records at a time
)

# Customize layout for better visualization
fig_neighborhood.update_traces(textposition='outside')
fig_neighborhood.update_layout(xaxis_title='Number of Users', yaxis_title='Neighborhood')
fig_neighborhood.update_yaxes(categoryorder='total descending')  # Sort by number of users (highest to lowest)

# Move x-axis to the top
fig_neighborhood.update_xaxes(side='top')

# ----- Obesity Levels Chart -----
filtered_df['BMI'] = filtered_df['weight'] / (filtered_df['height'] ** 2)
filtered_df = filtered_df[(filtered_df['BMI'].notnull()) & (filtered_df['weight'] <= 200)]
obesity_bins = [0, 18.5, 24.9, 29.9, 34.9, 39.9, float('inf')]
obesity_labels = ['Underweight', 'Normal Weight', 'Overweight', 'Obesity Grade 1', 'Obesity Grade 2', 'Obesity Grade 3']
filtered_df['obesity_level'] = pd.cut(filtered_df['BMI'], bins=obesity_bins, labels=obesity_labels)
obesity_counts = filtered_df['obesity_level'].value_counts().sort_index()
fig_obesity = px.bar(obesity_counts, x=obesity_counts.index, y=obesity_counts.values, labels={'x': 'Obesity Level', 'y': 'Quantity'}, title="Distribution of Obesity Levels", text=obesity_counts.values, color_discrete_sequence=['#FF9999'])
fig_obesity.update_traces(textposition='outside')
fig_obesity.update_layout(xaxis_title='Obesity Level', yaxis_title='Number of Users')

# ----- Display Charts Side by Side -----
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig)
with col2:
    st.plotly_chart(fig_age)
st.plotly_chart(fig_obesity)
st.plotly_chart(fig_permission)
st.plotly_chart(fig_neighborhood)

# Display data table if checkbox is checked
if st.checkbox('Show data'):
    st.dataframe(filtered_df)
