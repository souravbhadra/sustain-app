# Source: https://github.com/planetlabs/notebooks/blob/master/jupyter-notebooks/data-api-tutorials/search_and_download_quickstart.ipynb

import os
import time
import datetime
import requests
import urllib
import pandas as pd
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load the environment variable
load_dotenv(".env")
PLANET_KEY = os.getenv("PLANET_KEY")


class PlanetEngine():
    
    def __init__(
        self,
        geojson_geom,
        date,
    ):
        self.geojson_geom = geojson_geom
        self.date = date
        
        
    def format_date(
        self,
        date
    ):
        year = date.strftime("%Y")
        month = date.strftime("%m")
        day = date.strftime("%d")
        return f"{year}-{month}-{day}T00:00:00.000Z"
    
    
    def search_assets(
        self
    ):
        # Get images that overlap with our AOI 
        geometry_filter = {
            "type": "GeometryFilter",
            "field_name": "geometry",
            "config": self.geojson_geom
        }
        # Get images acquired within a date range
        # Create a 50 day interval of the given range
        start_date = self.date - datetime.timedelta(days=15)
        date_range_filter = {
            "type": "DateRangeFilter",
            "field_name": "acquired",
            "config": {
                "gte": self.format_date(start_date),
                "lte": self.format_date(self.date)
            }
        }
        # Get images that are highly visible (no haze or shadow)
        visibility_filter = {
            "type": "RangeFilter",
            "field_name": "visible_percent",
            "config": {
                "gte": 90
            }
        }
        # Combine geo, date, cloud filters
        combined_filter = {
            "type": "AndFilter",
            "config": [
                geometry_filter,
                date_range_filter,
                visibility_filter
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
        search_result_json = search_result.json()    
        # Extract metadata
        metadata = {
            'id': [],
            'visibility': [],
            'visibility_conf': []
        }
        for feature in search_result_json['features']:
            image_id = feature['id']
            visibility = feature['properties']['visible_percent']
            visibility_conf = feature['properties']['visible_confidence_percent']
            metadata['id'].append(image_id)
            metadata['visibility'].append(visibility)
            metadata['visibility_conf'].append(visibility_conf)
        # Create df and sort
        metadata = pd.DataFrame(metadata)
        metadata = metadata.sort_values(
            ['visibility', 'visibility_conf'],
            ascending=[False, False]
        )
        image_ids = metadata['id'].values.tolist()
        return image_ids
        

    def download_asset(
        self,
        image_id,
        out_dir
    ):
        # Create a URL of the image_id
        url = f"https://api.planet.com/data/v1/item-types/PSScene/items/{image_id}/assets"  
        # Returns JSON metadata for assets in this ID
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
        # Try until the link activates
        status = 'activating'
        while status == 'activating':
            # Get activation status result
            activation_status_result = requests.get(
                self_link,
                auth=HTTPBasicAuth(PLANET_KEY, '')
            )
            status = activation_status_result.json()["status"]
            time.sleep(10)
        # Image can be downloaded by making a GET with your Planet API key, from here:
        download_link = activation_status_result.json()["location"]
        out_path = os.path.join(out_dir, 'planet_img.tif')
        urllib.request.urlretrieve(download_link, out_path)
        
        return out_path
        
        