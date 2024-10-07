import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator import LoginError

# Page configuration
st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")

# Carregar credenciais do secrets.toml
USERNAME = st.secrets["app_user"]
PASSWORD = st.secrets["app_pwd"]

# Configuração manual de credenciais
credentials = {
    "usernames": {
        USERNAME: {
            "name": "admin",
            "password": PASSWORD,
            "email": "teste@teste.com"
        }
    }
}

# Creating the authentication object
authenticator = stauth.Authenticate(
    credentials,
    "kvd_dash_auth",  # Nome do cookie
    "kvd_dash_key",   # Chave do cookie
    cookie_expiry_days=30  # Tempo de expiração do cookie
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
        st.sidebar.title(f'Bem vindo, {st.session_state["name"]}!')  # Nome de exibição do usuário
        authenticator.logout('Logout', 'sidebar')  # Botão de logout na barra lateral
        st.write('Bem vindo!')
        st.title('Escolha uma página no menu lateral')
