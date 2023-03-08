import streamlit as st
import streamlit_authenticator as stauth

from multiapp import MultiApp
from apps import home, result

from utils import database as db

# Title stuffs
st.set_page_config(page_title="SustaiN", layout="wide")
st.sidebar.markdown("""
<style>
.big-font {
    font-size:50px !important;
}
</style>
""", unsafe_allow_html=True)
st.sidebar.markdown('<p class="big-font">SustaiN</p>', unsafe_allow_html=True)
st.sidebar.markdown(
    'Sustainable Nitrogen Management for Corn and Sorghum using Remote Sensing',
    unsafe_allow_html=True
)

## LOGIN
placeholder = st.empty()
users = db.fetch_all_users()
usernames = {}
for user in users:
    usernames[user["key"]] = {
        'name': user["name"],
        'password': user["password"]
    }
credentials = {
    "usernames": usernames
}
authenticator = stauth.Authenticate(
    credentials,
    cookie_name="sustain_app",
    key="abcdef",
    cookie_expiry_days=1
)
name, auth_status, _ = authenticator.login("Login", "main")

# Login Stuffs


if auth_status == False:
    st.error("Username/password is incorrect.")

if auth_status == None:
    st.warning("Please enter your username and password")
    
if auth_status:
    
    st.sidebar.header(f"Welcome _{name}_")
    authenticator.logout("Logout", "sidebar")
    st.session_state['username'] = name
    
    #with open('howto.md', 'r') as f:
    #    howto = f.read()
    
    #with st.sidebar.expander("How to use this app?"):
    #    st.markdown(howto)
    
    st.sidebar.markdown("[How to use this app?](https://duckduckgo.com)")

    app = MultiApp()

    app.add_app("Home", home.app)
    app.add_app("Result", result.app)
    app.run()
    
    
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)