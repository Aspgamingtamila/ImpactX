import ee
import geemap
import os

# Initialize Earth Engine
try:
    ee.Initialize()
    print("Earth Engine initialized successfully.")
except Exception as e:
    print("Earth Engine not authenticated. Please run 'earthengine authenticate' in the terminal.")
    import sys
    sys.exit(1)

# Define study area: Darjeeling District, West Bengal, India
print("Defining Study Area: Darjeeling...")
districts = ee.FeatureCollection("FAO/GAUL/2015/level2")
darjeeling = districts.filter(ee.Filter.eq('ADM2_NAME', 'Darjiling'))
roi = darjeeling.geometry()

# Years of interest
years = [2011, 2015, 2025]

# Output directory
out_dir = os.path.join(os.getcwd(), 'gee_exports')
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

# 1. Topographic Factors (DEM, Slope, Aspect)
# Using NASADEM (30m)
print("Processing Topography (DEM, Slope, Aspect)...")
dem = ee.Image("NASA/NASADEM_HGT/001").select('elevation').clip(roi)
slope = ee.Terrain.slope(dem)
aspect = ee.Terrain.aspect(dem)

# Export Topo layers
geemap.ee_export_image(dem, filename=os.path.join(out_dir, 'dem.tif'), scale=30, region=roi, file_per_band=False)
geemap.ee_export_image(slope, filename=os.path.join(out_dir, 'slope.tif'), scale=30, region=roi, file_per_band=False)
geemap.ee_export_image(aspect, filename=os.path.join(out_dir, 'aspect.tif'), scale=30, region=roi, file_per_band=False)

# 2. Meteorological (Rainfall - CHIRPS)
print("Processing Rainfall...")
chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")

for year in years:
    print(f"  Downloading Rainfall for {year}...")
    # We take the monsoon season (June to September) total rainfall
    monsoon_rain = chirps.filterDate(f'{year}-06-01', f'{year}-09-30').sum().clip(roi)
    geemap.ee_export_image(monsoon_rain, filename=os.path.join(out_dir, f'rainfall_{year}.tif'), scale=5566, region=roi, file_per_band=False)

# 3. Environmental (NDVI)
print("Processing NDVI...")
def get_ndvi(year):
    if year < 2015:
        # Landsat 7
        collection = ee.ImageCollection("LANDSAT/LE07/C02/T1_L2") \
            .filterBounds(roi) \
            .filterDate(f'{year}-01-01', f'{year}-12-31') \
            .filter(ee.Filter.lt('CLOUD_COVER', 20))
        
        def calc_ndvi(img):
            return img.normalizedDifference(['SR_B4', 'SR_B3']).rename('NDVI')
    else:
        # Sentinel-2 (post-2015)
        collection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
            .filterBounds(roi) \
            .filterDate(f'{year}-01-01', f'{year}-12-31') \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
        
        def calc_ndvi(img):
            return img.normalizedDifference(['B8', 'B4']).rename('NDVI')
            
    median_img = collection.median().clip(roi)
    return calc_ndvi(median_img)

for year in years:
    print(f"  Downloading NDVI for {year}...")
    ndvi = get_ndvi(year)
    # Using 30m scale for consistency, even though Sentinel is 10m
    geemap.ee_export_image(ndvi, filename=os.path.join(out_dir, f'ndvi_{year}.tif'), scale=30, region=roi, file_per_band=False)

# 4. Land Cover
print("Processing Land Cover...")
# WorldCover is available for 2020 and 2021. We'll use 2021 as a proxy.
worldcover = ee.ImageCollection("ESA/WorldCover/v200").first().clip(roi)
geemap.ee_export_image(worldcover, filename=os.path.join(out_dir, 'landcover.tif'), scale=30, region=roi, file_per_band=False)

print("Data extraction complete! Files saved in:", out_dir)
