import rasterio
import rasterio.mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
from shapely.geometry import shape
import json
import pyproj
from shapely.ops import transform
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import matplotlib.pyplot as plt
import cv2
from io import BytesIO
import base64

def reproject_raster(src_image_path, dst_crs='EPSG:4326'):
    with rasterio.open(src_image_path) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds
        )
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        dst_image_path = src_image_path.split('.')[0] + '_wgs.tif'
        with rasterio.open(dst_image_path, 'w', **kwargs) as dst:
            for i in range(1, src.count+1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest
                )
    return dst_image_path



def reproject_shape(geojson_geom, in_epsg, out_epsg):

    # Convert the GeoJSON geometry to a Shapely geometry
    geom = shape(geojson_geom)

    # Define the input and output projections
    in_proj = pyproj.CRS(f'EPSG:{in_epsg}')
    out_proj = pyproj.CRS(f'EPSG:{out_epsg}')
    
    # Define the transformation function
    project = pyproj.Transformer.from_crs(in_proj, out_proj, always_xy=True).transform

    reprojected_geom = transform(project, geom)
     
    # Convert the reprojected geometry to a GeoJSON geometry
    geojson_geom_proj = json.loads(json.dumps(reprojected_geom.__geo_interface__))
    
    return geojson_geom_proj

def calculate_index(img):
    nir = img[7, :, :]
    red = img[5, :, :]
    n_index = (nir-red)/(nir+red)
    return n_index

def clip_raster(planet_image_gcs_path, geojson_geom):
    # Read data
    src = rasterio.open(planet_image_gcs_path)
    # Convert the shapefile projection
    out_epsg = src.crs.to_epsg()
    geojson_geom_proj = reproject_shape(geojson_geom, '4326', out_epsg)
    # Clip the raster
    mask_img, _ = rasterio.mask.mask(
        src,
        [geojson_geom_proj],
        crop=True,
        filled=True
    )
    del src
    return mask_img

def save_img_png(out_path_png, img):
    scaler = MinMaxScaler()
    img = np.nan_to_num(img)
    img = scaler.fit_transform(img)
    cmap = plt.get_cmap('jet')
    img = cmap(img)
    img = (img*255).astype('int')
    cv2.imwrite(out_path_png, img)

def process_raster(planet_image_path, geojson_geom):
    
    # Change projection to GCS
    #planet_image_gcs_path = reproject_raster(planet_image_path)
    # Clip raster
    mask_img = clip_raster(planet_image_path, geojson_geom)
    # Calcualte the index
    mask_img_index = calculate_index(mask_img)
    # Save as png
    out_path_png = 'data/index.png'
    save_img_png(out_path_png, mask_img_index)


def png_to_binary(png_path):
    # Load the PNG image as a binary stream
    with open(png_path, 'rb') as f:
        image_binary = BytesIO(f.read())
    # Convert the binary stream to a base64-encoded string
    image_base64 = base64.b64encode(image_binary.getvalue()).decode('utf-8')
    return image_base64
