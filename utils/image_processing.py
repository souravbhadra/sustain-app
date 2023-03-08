import rasterio
import rasterio.mask
from shapely.geometry import shape
import json
import pyproj
from shapely.ops import transform
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import matplotlib.pyplot as plt
import cv2

from utils.geoprocessing import reproject_shape



class ImageProcessor():
    
    def __init__(
        self,
        planet_image_path,
        geojson_geom
    ):
        self.planet_image_path = planet_image_path
        self.geojson_geom = geojson_geom
        
        # Clip the raster
        self.src = rasterio.open(planet_image_path)
        # Convert the shapefile projection
        out_epsg = self.src.crs.to_epsg()
        geojson_geom_proj = reproject_shape(
            self.geojson_geom, '4326', out_epsg
        )
        # Clip the raster
        self.mask_img, _ = rasterio.mask.mask(
            self.src,
            [geojson_geom_proj],
            crop=True,
            filled=True,
            all_touched=True
        )
        self.mask_img = self.mask_img.astype('float')
        self.mask_img[self.mask_img==self.src.nodata] = np.nan
    
    
    def ndvi(
        self
    ):
        nir = self.mask_img[7, :, :]
        red = self.mask_img[5, :, :]
        ndvi = (nir-red)/(nir+red)
        return ndvi
    
    
    def ndre(
        self
    ):
        nir = self.mask_img[7, :, :]
        rededge = self.mask_img[6, :, :]
        ndre = (nir-rededge)/(nir+rededge)
        return ndre


def calculate_nindex_stats(
    n_index
):
    # Create a copy of the array
    n_index_copy = np.copy(n_index)
    stats = [
        np.nanmin(n_index_copy),
        np.nanpercentile(n_index_copy, 25),
        np.nanmean(n_index_copy),
        np.nanpercentile(n_index_copy, 75),
        np.nanmax(n_index_copy)
    ]
    return stats