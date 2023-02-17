import streamlit as st
import streamlit_authenticator as stauth

from multiapp import MultiApp
from apps import home, result

from utils import database as db


# Title stuffs
st.set_page_config(page_title="SustaiN", layout="wide")
st.title("SustaiN")
st.write(
    """
    A Decision Support System for Sustainable Nitrogen Management in Corn and Sorghum using Remote Sensing
    """
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
    cookie_expiry_days=30
)
name, auth_status, _ = authenticator.login("Login", "main")

# Login Stuffs


if auth_status == False:
    st.error("Username/password is incorrect.")

if auth_status == None:
    st.warning("Please enter your username and password")
    
if auth_status:
    
    st.sidebar.title(f"Welcome {name}")
    authenticator.logout("Logout", "sidebar")
        

    app = MultiApp()

    app.add_app("Home", home.app)
    app.add_app("Result", result.app)
    app.run()