import streamlit as st

from multiapp import MultiApp
from apps import home, result

from utils import image_placement
from utils import authentication



# Page config
st.set_page_config(
    page_title="SustaiN",
    page_icon='images\icon.png',
    layout="wide"
)


if 'logged_in' not in st.session_state:
    image_placement.insert_image('images\logo.png', False)
    st.session_state['logged_in'] = False
    authentication.show_login_page()
else:
    if st.session_state['logged_in']:
        image_placement.insert_image('images\logo.png', True, width=100)
        name = st.session_state.username
        st.sidebar.header(f"Welcome _{name}_")
        st.sidebar.markdown("[How to use this app?](https://www.youtube.com/)")
        app = MultiApp()
        app.add_app("Home", home.app)
        app.add_app("Result", result.app)
        app.run()
    else:
        image_placement.insert_image('images\logo.png', False)
        authentication.show_login_page()


    
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)