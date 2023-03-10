import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import zipfile
from jinja2 import Template
import tempfile
import shutil
import os

from utils import image_management as im


def colorize(
    array
):
    # Source: https://www.linkedin.com/pulse/visualize-dem-interactive-map-chonghua-yin/?trk=related_artice_Visualize%20DEM%20in%20An%20Interactive%20Map_article-card_title
    normed_data = (array - array.min()) / (array.max() - array.min())    
    cm = plt.cm.get_cmap('rainbow')    
    return cm(normed_data)


def apply_veg_mask(
    ndre,
    ndvi,
    ndvi_slider
):
    start_ndvi = ndvi_slider[0]
    end_ndvi = ndvi_slider[1]
    veg = ((ndvi >= start_ndvi) & (ndvi <= end_ndvi)) * 1
    ndre = ndre * veg
    ndre[ndre==0.0] = np.nan
    return ndre


def zip_to_binary(m, metadata):
    with tempfile.TemporaryDirectory() as temp_dir:
        # Get the file paths of individual files
        file_paths = [
            save_folium(m, temp_dir),
            save_style_css(temp_dir),
            save_report_html(metadata, temp_dir)
        ]
        # Create a zip file named 'report.zip' in the current directory
        zip_path = os.path.join(temp_dir, 'report.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add each file in the list to the zip file
            for file_path in file_paths:
                zip_file.write(
                    os.path.abspath(file_path),
                    os.path.basename(file_path)
                )
        # Open the zip as binary and return it        
        with open(zip_path, 'rb') as f:
            zip_bytes = f.read()
    return zip_bytes


def save_folium(
    m,
    temp_dir
):    
    html_file_path = os.path.join(temp_dir, 'map.html')
    m.save(html_file_path)
    return html_file_path

def save_style_css(
    temp_dir
):    
    src_file = os.path.join(os.getcwd(), 'utils', 'report_style.css')
    dst_file = os.path.join(temp_dir, 'style.css')
    shutil.copy(src_file, dst_file)
    return dst_file

def save_report_html(
    metadata,
    temp_dir
):  
    sutain_logo_html = im.img_to_html(
        os.path.join(
            os.getcwd(),
            'images',
            'logo.png'
        ),
        margin=(0, 0, 30, 0),
        width='auto'
    )
    cmap_html = im.img_to_html(
        os.path.join(
            os.getcwd(),
            'images',
            'cmap.png'
        ),
        margin=(0, 0, 0, 0),
        width=100
    )
    bottom_logo_html = im.img_to_html(
        os.path.join(
            os.getcwd(),
            'images',
            'report-bottom-logo.png'
        ),
        margin=(0, 0, 0, 0),
        width=100
    )
    metadata['SUSTAIN_LOGO'] = sutain_logo_html
    metadata['CMAP_HTML'] = cmap_html
    metadata['BOTTOM_LOGO_HTML'] = bottom_logo_html
    template_fpath = os.path.join(
        os.getcwd(),
        'utils',
        'report_template.html'
    )
    # Load the HTML template
    with open(template_fpath) as f:
        template = Template(f.read())
    # Render the template with the data
    output = template.render(metadata)
    # Save the rendered HTML to a file
    out_path = os.path.join(temp_dir, 'REPORT.html')
    with open(out_path, 'w') as f:
        f.write(output)
    return out_path