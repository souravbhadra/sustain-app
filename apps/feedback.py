import os
import streamlit as st


def app():
    
    st.header(":mailbox: Please give your feedback here!")
    
    contact_form = """
    <form action="https://formsubmit.co/sourav.bhadra@slu.edu" method="POST">
        <input type="text" name="name" placeholder="Your full name" required>
        <input type="email" name="email" placeholder="Your email" required>
        <textarea name="message" placeholder="Your message here"></textarea>
        <button type="submit">Send</button>
    </form>
    
    """
    
    st.markdown(contact_form, unsafe_allow_html=True)
    
    css_file = os.path.join(os.getcwd(), 'utils', 'feedback_style.css')
    with open(css_file) as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )