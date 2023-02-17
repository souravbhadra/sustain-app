# Source: https://github.com/planetlabs/notebooks/blob/master/jupyter-notebooks/data-api-tutorials/search_and_download_quickstart.ipynb

import os
import time
import datetime
import requests
import urllib
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load the environment variable
load_dotenv(".env")
PLANET_KEY = os.getenv("PLANET_KEY")



def get_formatted_date(date):
    year = date.strftime("%Y")
    month = date.strftime("%m")
    day = date.strftime("%d")
    return f"{year}-{month}-{day}T00:00:00.000Z"


def get_image_ids(geojson_geom, date):
    
    # Get images that overlap with our AOI 
    geometry_filter = {
        "type": "GeometryFilter",
        "field_name": "geometry",
        "config": geojson_geom
    }
    
    # Get images acquired within a date range
    # Create a 10 day interval of the given range
    start_date = date - datetime.timedelta(days=10)
    date_range_filter = {
        "type": "DateRangeFilter",
        "field_name": "acquired",
        "config": {
            "gte": get_formatted_date(start_date),
            "lte": get_formatted_date(date)
        }
    }
    
    # Only get images which have <50% cloud coverage
    cloud_cover_filter = {
        "type": "RangeFilter",
        "field_name": "cloud_cover",
        "config": {
            "lte": 0.5
        }
    }
    
    # Combine geo, date, cloud filters
    combined_filter = {
        "type": "AndFilter",
        "config": [
            geometry_filter,
            date_range_filter,
            cloud_cover_filter
        ]
    }
    
    # API request object
    search_request = {
        "item_types": ["PSScene"], 
        "filter": combined_filter
    }
    
    # Fire off the POST request
    search_result = requests.post(
        "https://api.planet.com/data/v1/quick-search",
        auth=HTTPBasicAuth(PLANET_KEY, ''),
        json=search_request
    )
    # Get the geojsons
    geojson = search_result.json()
        
    # Extract image IDs only
    image_ids = [feature['id'] for feature in geojson['features']]
    
    return image_ids


def get_download_link(image_id):
    
    # Create a URL of the image_id
    url = f"https://api.planet.com/data/v1/item-types/PSScene/items/{image_id}/assets"
    
    # Returns JSON metadata for assets in this ID. Learn more: planet.com/docs/reference/data-api/items-assets/#asset
    result = requests.get(
        url,
        auth=HTTPBasicAuth(PLANET_KEY, '')
    )
    
    # Get activation link
    links = result.json()[u"ortho_analytic_8b_sr"]["_links"]
    self_link = links["_self"]
    activation_link = links["activate"]
    
    # Request activation of the 'ortho_analytic_8b_sr' asset:
    activate_result = requests.get(
        activation_link,
        auth=HTTPBasicAuth(PLANET_KEY, '')
    )
    
    status = 'activating'
    while status == 'activating':
        # Get activation status result
        activation_status_result = requests.get(
            self_link,
            auth=HTTPBasicAuth(PLANET_KEY, '')
        )
        status = activation_status_result.json()["status"]
        print(status)
        time.sleep(5)
            
    # Image can be downloaded by making a GET with your Planet API key, from here:
    download_link = activation_status_result.json()["location"]
    
    return download_link


def download_planet_image(download_link, out_dir):
    out_path = os.path.join(out_dir, 'planet_img.tif')
    urllib.request.urlretrieve(download_link, out_path)
    return out_path
    
  

def get_planet_image_path(geojson_geom, date, out_dir):
    
    # Get the image_ids from the given filter values
    image_ids = get_image_ids(geojson_geom, date)
    
    # Get the download link
    download_link = get_download_link(image_ids[0])
    
    # Download the image and get the path
    planet_img_path = download_planet_image(download_link, out_dir)
    
    return planet_img_path



