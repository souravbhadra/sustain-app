import os
import streamlit as st
import pyrebase
from dotenv import load_dotenv

load_dotenv(".env")
# Load env variables
FBASE_CONFIG = {
    'apiKey': os.getenv("FBASE_API_KEY"),
    'authDomain': os.getenv("FBASE_AUTH_DOMAIN"),
    'projectId': os.getenv("FBASE_PROJECT_ID"),
    'storageBucket': os.getenv("FBASE_STORAGE_BUCKET"),
    'messagingSenderId': os.getenv("FBASE_MESSAGING_SENDER_ID"),
    'appId': os.getenv("FBASE_APP_ID"),
    'measurementId': os.getenv("FBASE_MEASUREMENT_ID"),
    'databaseURL': os.getenv("FBASE_DATABASE_URL")
}

# Authenticate firebase and database
firebase = pyrebase.initialize_app(FBASE_CONFIG)
auth = firebase.auth()
db = firebase.database()


def get_full_name_from_db(
    email
):
    query = db.child("user_info").order_by_child("email").equal_to(email).limit_to_first(1).get()
    for i in query.each():
        first_name = i.val()['first_name']
        middle_name = i.val()['middle_name']
        last_name = i.val()['last_name']
        if middle_name is None:
            full_name = f"{first_name} {last_name}"
        else:
            full_name = f"{first_name} {middle_name} {last_name}"
    return full_name


def logged_in_clicked(
    email,
    password
):
    try:
        user = auth.sign_in_with_email_and_password(
            email,
            password
        )
        st.session_state['username'] = get_full_name_from_db(email)
        st.session_state['logged_in'] = True
    except:
        st.session_state['logged_in'] = False
        st.error('Invalid user name or password')
    


def show_login_page():
    placeholder = st.container()
    with placeholder:
        if st.session_state.logged_in == False:
            email = st.text_input(
                label='Enter your email *'
            )
            password = st.text_input(
                label='Enter your password',
                type="password"
            )
            st.button(
                label='Sign In',
                on_click=logged_in_clicked,
                args=(email, password)
            )
            signup_link = '<a href="https://sustain-reg.herokuapp.com/" target="_self">New user? Sign Up here!</a>'
            st.markdown(signup_link, unsafe_allow_html=True)