import os
import pickle
import streamlit as st
import folium
from dotenv import load_dotenv
from streamlit_folium import st_folium

# Load the environment variable
load_dotenv(".env")
MAPBOX_KEY = os.getenv("MAPBOX_KEY")
tileset_ID_str = "satellite-streets-v12"
mapbox_url = f"https://api.mapbox.com/styles/v1/mapbox/{tileset_ID_str}/tiles/{{z}}/{{x}}/{{y}}@2x?access_token={MAPBOX_KEY}"

def app():
    # Read data
    image_bounds_path = 'data/image_bounds.pkl'
    if os.path.exists(image_bounds_path):
        with open(image_bounds_path, 'rb') as f:
            image_bounds = pickle.load(f)
        #os.remove(image_bounds_path)
        index_path = 'data/index.png'
        
        # Draw the map
        m = folium.Map(
            location=image_bounds[0],
            zoom_start=15,
            tiles=None
        )
        folium.TileLayer(mapbox_url, name='Satellite Basemap', attr='Mapbox').add_to(m)
        folium.raster_layers.ImageOverlay(index_path, bounds=image_bounds).add_to(m)
        folium.LayerControl().add_to(m)

        st_folium(
            m,
            width=900,
            height=500
        )
        
    else:
        st.sidebar.warning("Please submit your request in the Home page")
    
    
    