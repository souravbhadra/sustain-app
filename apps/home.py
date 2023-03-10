import os
import tempfile
import time
import datetime
import streamlit as st
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv
from PIL import Image

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
    date_help = "The date should be at least 7 days prior to the current date. We will \
        search images between the date you have selected and 15 days prior to that date.\
        Your selected date can NOT be prior to 2022."
    maximum_date = datetime.datetime.now()-datetime.timedelta(days=7)
    minimum_date = datetime.date(2022, 1, 1)
    date = st.sidebar.date_input(
        "Date",
        value=maximum_date,
        min_value=minimum_date,
        max_value=maximum_date, 
        help=date_help
    )
    date_str = date.strftime("%Y-%m-%d")
    st.session_state['request_date'] = date_str   

    
    if 'map_zoom' not in st.session_state:
        map_zoom = 4
    else:
        map_zoom = st.session_state.map_zoom
    if 'map_lat' not in st.session_state:
        map_lat = 39
    else:
        map_lat = st.session_state.map_lat
    if 'map_lon' not in st.session_state:
        map_lon = -100
    else:
        map_lon = st.session_state.map_lon
    
    # Draw the map
    m = folium.Map(
        location=[map_lat, map_lon], #[39, -100]
        zoom_start=map_zoom,
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
        height=500
    )
    
    last_draw = output["all_drawings"]

    # Check the polygon
    if last_draw is None or len(last_draw) == 0:
        st.sidebar.warning(
            """
            Define a polygon using the ⬛ button on the left pan of map. The polygon should
            be less than 5 Sq Km or 1235 acres.
            """
        )
        request_button = st.sidebar.button(
            label='Submit Request',
            help='You cannot submit a request unless you have specified a valid polygon',
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
        if area > 50:
            st.sidebar.warning(
                f"""
                The polygon is too large ({area:.2f} Sq Km), it has to be less than 5 Sq
                Km or 1235 acres.
                """
            )
            request_button = st.sidebar.button(
                label='Submit Request',
                help='You cannot submit a request unless you have specified a valid polygon',
                disabled=True
            )
        else:
            st.session_state["aoi_area"] = area
            st.sidebar.success(
                f"""
                Your polygon is {area:.2f} Sq Km and the selected date is {date_str}.
                Click `Submit Request` to start processing. Please be patient as it might
                take 15-20 minutes.
                """
            )
            #st.sidebar.write(coordinates)
            request_button = st.sidebar.button(
                label='Submit Request',
                help='Submit the request for processing the result map',
                disabled=False
            )
            if request_button:
                with st.spinner('Running'):
                    with tempfile.TemporaryDirectory() as tmpdir:
                        
                        since = time.time()
                        # Define the planet engine and search for assets
                        planet_engine = pb.PlanetEngine(
                            geojson_geom, date
                        )
                        image_ids = planet_engine.search_assets()
                        
                        planet_img_path = planet_engine.download_asset(
                            image_ids[0], tmpdir
                        )
                        image_processor = ip.ImageProcessor(planet_img_path, geojson_geom)
                        
                        ndvi = image_processor.ndvi()
                        ndre = image_processor.ndre()
                        
                        image_processor.close_rasterio()
                        
                        st.session_state['image_bounds'] = gp.get_geojson_bounds(geojson_geom)
                        st.session_state['NDVI'] = ndvi
                        st.session_state['NDRE'] = ndre
                            
                        time_elapsed = (time.time()-since)/60.0
                        
                        st.balloons()
                        st.success(
                            f"""
                            Processing finishsed in {time_elapsed:.2f} minutes. Go to
                            `Result` now.
                            """
                        )
                        
                        st.session_state['map_zoom'] = output["zoom"]
                        st.session_state['map_lat'] = output["center"]["lat"]
                        st.session_state['map_lon'] = output["center"]["lng"]