import pickle
import json
from geopy import Nominatim
import pyproj
from shapely.geometry import shape
import shapely.ops as ops
from shapely.geometry.polygon import Polygon
from functools import partial
from shapely.ops import transform

import warnings
warnings.filterwarnings("ignore")


def geocoder(address):
    """Returns the geocoded coordinates of a given text address

    Args:
        address (str): An address text

    Returns:
        tuple: (Latitude, Longitude)
    """
    locator = Nominatim(user_agent="myGeocoder")
    location = locator.geocode(address)
    return location.latitude, location.longitude


def reproject_shape(
    geojson_geom,
    in_epsg,
    out_epsg
):
    # Convert the GeoJSON geometry to a Shapely geometry
    geom = shape(geojson_geom)
    # Define the input and output projections
    in_proj = pyproj.CRS(f'EPSG:{in_epsg}')
    out_proj = pyproj.CRS(f'EPSG:{out_epsg}')
    # Define the transformation function  
    project = pyproj.Transformer.from_crs(
        in_proj, out_proj, always_xy=True
    ).transform
    reprojected_geom = transform(project, geom)
    # Convert the reprojected geometry to a GeoJSON geometry
    geojson_geom_proj = json.loads(
        json.dumps(reprojected_geom.__geo_interface__)
    )
    return geojson_geom_proj


def calculate_area(geojson_geom):
    """Calcualte the approximate area of a given geojson polygon

    Args:
        geojson_geom (GeoJSON): A GeoJSON polygon

    Returns:
        float: area in sq km
    """
    geom = Polygon(geojson_geom['coordinates'][0])

    geom_area = ops.transform(
        partial(
            pyproj.transform,
            pyproj.Proj(init='EPSG:4326'),
            pyproj.Proj(
                proj='aea',
                lat_1=geom.bounds[1],
                lat_2=geom.bounds[3]
            )
        ),
        geom)

    # Convert area from sqm to sqkm
    area = geom_area.area / 1e6
    return area


def get_geojson_bounds(geojson_geom):
    geom = shape(geojson_geom)
    bounds = geom.bounds
    image_bounds = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
    #out_path = 'data/image_bounds.pkl'
    #with open(out_path, 'wb') as f:
    #    pickle.dump(image_bounds, f)
    return image_bounds