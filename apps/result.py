import os
import time
import tempfile
from PIL import Image
import numpy as np
import numpy.ma as ma
import streamlit as st
import folium
from dotenv import load_dotenv
from streamlit_folium import st_folium
import matplotlib.pyplot as plt

from utils import result_generation as rg
from utils import image_processing as ip
from utils import image_placement


# Load the environment variable
load_dotenv(".env")
MAPBOX_KEY = os.getenv("MAPBOX_KEY")
tileset_ID_str = "satellite-streets-v12"
mapbox_url = f"https://api.mapbox.com/styles/v1/mapbox/{tileset_ID_str}/tiles/{{z}}/{{x}}/{{y}}@2x?access_token={MAPBOX_KEY}"



def app():
    if 'NDRE' not in st.session_state:
        st.sidebar.error("Please submit your request in the Home page")
    else:
        
        ndvi = st.session_state.NDVI
        ndre = st.session_state.NDRE
        
        ndvi_slider = st.sidebar.slider(
            label='Adjust this scale to remove unwanted objects from your results',
            min_value=-1.0,
            max_value=1.0,
            value=(0.2, 0.8)            
        )
        
        n_index = rg.apply_veg_mask(ndre, ndvi, ndvi_slider)
        
        n_index = ma.masked_invalid(n_index)
        n_index_color = rg.colorize(n_index)
        image_bounds = st.session_state.image_bounds
        
        # Draw the map
        map_zoom = st.session_state.map_zoom
        map_lat = st.session_state.map_lat
        map_lon = st.session_state.map_lon
        m = folium.Map(
            location=[map_lat, map_lon],
            zoom_start=map_zoom,
            tiles=None
        )
        
        folium.TileLayer(mapbox_url, name='Satellite Basemap', attr='Mapbox').add_to(m)
        folium.raster_layers.ImageOverlay(n_index_color, bounds=image_bounds, attr='N-Index').add_to(m)
        folium.LayerControl().add_to(m)

        output = st_folium(
            m,
            width=900,
            height=500
        )
        
        #cmap = Image.open('apps\cmap.png')
        #st.sidebar.image(cmap)
        #st.sidebar.markdown(cmap)
        image_placement.insert_image(
            os.path.join(os.getcwd(), 'images', 'cmap.png'),
            sidebar=True,
            margin=(0, 0, 0, 0),
            width=100
        )
        col1, col2, col3 = st.sidebar.columns(3)
        n_index_stats = ip.calculate_nindex_stats(n_index)
        with col1:
            st.markdown(
                f"<p style='text-align: left'>{n_index_stats[0]:.2f}</p>",
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"<p style='text-align: center'>{n_index_stats[2]:.2f}</p>",
                unsafe_allow_html=True
            )
        with col3:
            st.markdown(
                f"<p style='text-align: right'>{n_index_stats[4]:.2f}</p>",
                unsafe_allow_html=True
            )
        
            
        metadata = {
            'USERNAME': st.session_state.username,
            'INDEX_MIN': f"{n_index_stats[0]:.2f}",
            'INDEX_25': f"{n_index_stats[1]:.2f}",
            'INDEX_MEAN': f"{n_index_stats[2]:.2f}",
            'INDEX_75': f"{n_index_stats[3]:.2f}",
            'INDEX_MAX': f"{n_index_stats[4]:.2f}",
            'REQUEST_DATE': st.session_state.request_date,
            'AOI_AREA': f"{st.session_state.aoi_area:.2f}",
            'IMAGE_DATE': "2022-24-21",
            'IMAGE_TIME': "2022-24-21"
        }
            
       
        st.download_button(
            label='Download Report',
            data=rg.zip_to_binary(m, metadata),
            file_name='report.zip',
            mime='application/zip',
            help='Saves the report as zip, open the REPORT.html to see results.'
        )
            
            
        