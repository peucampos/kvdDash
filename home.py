import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from streamlit_authenticator import LoginError

# Page configuration
st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")

# Loading authentication settings
with open("config.yaml", "r") as ymlfile:
    config = yaml.load(ymlfile, Loader=SafeLoader)

# Creating the authentication object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    cookie_expiry_days=config['cookie']['expiry_days']
)

def authenticate_user():
    try:
        authenticator.login('main')
    except LoginError as e:
        st.error(e)

    if st.session_state.get("authentication_status"):
        return True
    elif st.session_state.get("authentication_status") is False:
        st.error('Usuário ou senha inválidos')
        return False
    elif st.session_state.get("authentication_status") is None:
        st.warning('Entre com suas credenciais')
        return False

# Attempting login on home page
if __name__ == "__main__":
    if authenticate_user():
        st.sidebar.title(f'Bem vindo, {st.session_state["name"]}!')
        authenticator.logout('Logout', 'sidebar')  # Logout button in the sidebar
        st.write('Bem vindo!')
        st.title('Escolha uma página no menu lateral')

# In your internal pages, you can use the authenticate_user function like this:
# if not authenticate_user():
#     st.experimental_rerun()