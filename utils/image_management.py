import streamlit as st
import base64

@st.cache_data()
def get_base64_of_bin_file(png_file):
    with open(png_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def img_to_html(
    png_file,
    margin=(0, 0, 0, 0),
    width='auto'
):
    img_html = "<img src='data:image/png;base64,{}' class='img-fluid' style='margin: {}px {}px {}px {}px;' width={}%>".format(
      get_base64_of_bin_file(png_file),
      margin[0],
      margin[1],
      margin[2],
      margin[3],
      width
    )
    return img_html

def insert_image(
    png_file,
    sidebar=False,
    margin=(0, 0, 30, 0),
    width='auto'
):
    if sidebar:
        st.sidebar.markdown(
            img_to_html(png_file, margin, width),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            img_to_html(png_file, margin, width),
            unsafe_allow_html=True,
        )