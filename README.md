# Landslide Susceptibility Mapping: Darjeeling Himalayas

This project contains the complete workflow for generating a Landslide Susceptibility Zonation map for the Darjeeling Himalayas using a Multi-Criteria Decision Analysis (MCDA) approach. It utilizes **Google Earth Engine (GEE)** for satellite data extraction and **Python** for hydrological processing and weighted overlay analysis.

## Project Structure

* `01_gee_data_export.js`: Google Earth Engine JavaScript code. Copy and paste this into the [GEE Code Editor](https://code.earthengine.google.com/) to automatically extract and export DEM, Slope, Aspect, Rainfall (2011, 2015, 2025), NDVI, and Land Cover directly to your Google Drive.
* `02_drainage_density.py`: A Python script utilizing WhiteboxTools to calculate flow accumulation, extract stream networks from the DEM, and compute the drainage density.
* `03_susceptibility_model.py`: A Python script using `rasterio` and `numpy` to reclassify all spatial layers into a 1-5 risk scale and perform the final Weighted Overlay math to generate the susceptibility map.
* `preview_map.html`: An interactive Web GIS Dashboard built with Leaflet.js to preview the study area and output layers.

## Methodology

This model combines topographic, meteorological, and environmental factors with the following example weighting scheme:
1. **Slope** (35%): Derived from NASADEM (30m).
2. **Rainfall** (25%): Monsoon accumulation from CHIRPS data.
3. **NDVI/Land Use** (20%): Extracted from Sentinel-2/Landsat and ESA WorldCover.
4. **Drainage Density** (20%): Hydrologically modeled from the DEM.

### How to Use
1. Run the `.js` script in the Google Earth Engine web browser and export the GeoTIFFs to your Drive.
2. Download the GeoTIFFs to a local `gee_exports` folder.
3. Run the Python scripts to generate the final `susceptibility_map.tif`.

## Preview
Open `preview_map.html` in any web browser to see the interactive mapping interface.
