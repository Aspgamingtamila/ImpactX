import rasterio
import numpy as np
import os
import matplotlib.pyplot as plt

in_dir = os.path.join(os.getcwd(), 'gee_exports')
proc_dir = os.path.join(os.getcwd(), 'processed_layers')
out_dir = os.path.join(os.getcwd(), 'final_output')

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

def read_raster(filepath):
    with rasterio.open(filepath) as src:
        data = src.read(1)
        meta = src.meta
    return data, meta

# 1. Read input layers
# For simplicity in this demo, we'll use a single year (e.g. 2025)
print("Loading layers...")
slope, meta = read_raster(os.path.join(in_dir, 'slope.tif'))
rain, _ = read_raster(os.path.join(in_dir, 'rainfall_2025.tif'))
ndvi, _ = read_raster(os.path.join(in_dir, 'ndvi_2025.tif'))
lc, _ = read_raster(os.path.join(in_dir, 'landcover.tif'))
dd, _ = read_raster(os.path.join(proc_dir, 'drainage_density.tif'))

# Ensure nodata regions are masked out
nodata = meta.get('nodata', -9999)

def reclassify_slope(s):
    # Reclassify Slope (1-5)
    r = np.ones_like(s)
    r[(s >= 10) & (s < 20)] = 2
    r[(s >= 20) & (s < 30)] = 3
    r[(s >= 30) & (s < 45)] = 4
    r[s >= 45] = 5
    r[s == nodata] = 0
    return r

def reclassify_ndvi(n):
    # Reclassify NDVI (Bare=High risk, Forest=Low risk)
    r = np.ones_like(n) * 5
    r[(n > 0.2) & (n <= 0.4)] = 4
    r[(n > 0.4) & (n <= 0.6)] = 3
    r[(n > 0.6) & (n <= 0.8)] = 2
    r[n > 0.8] = 1
    r[n == nodata] = 0
    return r

# (In a real project, we would do this carefully for Rainfall, Landcover, and Drainage Density based on local statistics)
# For the demo, we generate normalized pseudo-risk layers.
def normalize_to_1_5(data):
    # Ignore nodata
    valid = data[data != nodata]
    if len(valid) == 0: return np.ones_like(data)
    min_val, max_val = np.percentile(valid, 5), np.percentile(valid, 95)
    norm = (data - min_val) / (max_val - min_val) * 4 + 1
    norm = np.clip(norm, 1, 5)
    norm[data == nodata] = 0
    return np.round(norm)

print("Reclassifying layers...")
slope_r = reclassify_slope(slope)
ndvi_r = reclassify_ndvi(ndvi)
rain_r = normalize_to_1_5(rain)
dd_r = normalize_to_1_5(dd)

# 2. Assign Weights and Calculate Susceptibility
# Slope: 0.35, Rain: 0.25, LULC(Proxy here via NDVI): 0.20, DD: 0.20
print("Performing Weighted Overlay...")
weights = {'slope': 0.35, 'rain': 0.25, 'ndvi': 0.20, 'dd': 0.20}

# Create a mask where any data is 0 (nodata)
mask = (slope_r == 0) | (ndvi_r == 0) | (rain_r == 0) | (dd_r == 0)

susceptibility = (slope_r * weights['slope'] + 
                 rain_r * weights['rain'] + 
                 ndvi_r * weights['ndvi'] + 
                 dd_r * weights['dd'])

susceptibility[mask] = nodata

# 3. Save Final Raster
meta.update(dtype=rasterio.float32, nodata=nodata)
final_tif = os.path.join(out_dir, 'susceptibility_map.tif')
with rasterio.open(final_tif, 'w', **meta) as dst:
    dst.write(susceptibility.astype(rasterio.float32), 1)

print("Susceptibility map saved to:", final_tif)

# 4. Generate a quick plot
plt.figure(figsize=(10, 10))
sus_masked = np.ma.masked_where(susceptibility == nodata, susceptibility)
plt.imshow(sus_masked, cmap='RdYlGn_r')
plt.colorbar(label='Susceptibility Index')
plt.title('Landslide Susceptibility - Darjeeling Himalayas')
plt.savefig(os.path.join(out_dir, 'susceptibility_preview.png'))
print("Preview map saved!")
