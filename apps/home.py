import os
import tempfile
import time
import streamlit as st
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv

from utils import database as db
from utils import geoprocessing as gp
from utils import planet_backend as pb
from utils import image_processing as ip



# Load the environment variable
load_dotenv(".env")
MAPBOX_KEY = os.getenv("MAPBOX_KEY")
tileset_ID_str = "satellite-streets-v12"
mapbox_tile_URL = f"https://api.mapbox.com/styles/v1/mapbox/{tileset_ID_str}/tiles/{{z}}/{{x}}/{{y}}@2x?access_token={MAPBOX_KEY}"


def app():
    
    # Date input
    date = st.sidebar.date_input(
        "Date",
        value=None,
        min_value=None,
        max_value=None, 
        help=None
    )
    
    # Draw the map
    m = folium.Map(
        location=[39, -100],
        zoom_start=4,
        tiles=mapbox_tile_URL,
        attr='Mapbox'
    )
    
    folium.plugins.Geocoder().add_to(m)
    folium.plugins.Draw(
        draw_options={
            'polyline': False,
            'polygon': False,
            'circle': False,
            'marker': False,
            'circlemarker': False
        }
    ).add_to(m)
    
    output = st_folium(
        m,
        width=900,
        height=500,
        returned_objects=["all_drawings"]
    )
    last_draw = output["all_drawings"]

    # Check the polygon
    if last_draw is None or len(last_draw) == 0:
        st.sidebar.warning("Please define your Area of Interest (AOI) using the black square box on the left pan of the basemap. The AOI should not exceed 5 Sq Km or 1235 acres.")
        request_button = st.sidebar.button(
            label='Submit Request',
            help='You cannot submit a request unless you have specified a valid AOI',
            disabled=True
        )
    else:
        # Get the coordinates from the last drawn polygon
        coordinates = last_draw[-1]['geometry']['coordinates']
        geojson_geom = {
            "type": "Polygon",
            "coordinates": coordinates
            }
        
        # Calculate the area of the drawn polygon
        area = gp.calculate_area(geojson_geom)
        if area > 5:
            st.sidebar.warning(f"The AOI is too large ({area:.2f} Sq Km), it has to be less than 5 Sq Km or 500 acres")
            request_button = st.sidebar.button(
                label='Submit Request',
                help='You cannot submit a request unless you have specified a valid AOI',
                disabled=True
            )
        else:
            st.sidebar.warning(f"Your AOI is {area:.2f} Sq Km and you are ready to start processing.")
            #st.sidebar.write(coordinates)
            request_button = st.sidebar.button(
                label='Submit Request',
                help='Submit the request for processing the result map',
                disabled=False
            )
            if request_button:
                st.sidebar.info('Processing started. Please be patient! It can take as long as 15 minutes.')
                # Delete if there is any image_bounds.pkl in the data folder
                image_bounds_path = 'data/image_bounds.pkl'
                if os.path.exists(image_bounds_path):
                    os.remove(image_bounds_path)
                with st.spinner('Running'):
                    with tempfile.TemporaryDirectory() as tmpdir:
                        
                        since = time.time()
                        planet_img_path = pb.get_planet_image_path(geojson_geom, date, tmpdir)
                        time_elapsed = (time.time()-since)/60.0
                        st.sidebar.info(f'Image downloaded in {time_elapsed:.2f} minutes')
                        
                        since = time.time()
                        ip.process_raster(planet_img_path, geojson_geom)
                        time_elapsed = (time.time()-since)/60.0
                        st.sidebar.info(f"Index Calculated in {time_elapsed:.2f} minutes")
                        
                        gp.save_geojson_bounds(geojson_geom)
                        st.balloons()
                        st.sidebar.success("Processing Finishsed. Go to result now!")