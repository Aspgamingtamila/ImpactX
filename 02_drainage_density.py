import whitebox
import os

wbt = whitebox.WhiteboxTools()

# Directories
in_dir = os.path.join(os.getcwd(), 'gee_exports')
out_dir = os.path.join(os.getcwd(), 'processed_layers')
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

dem_file = os.path.join(in_dir, 'dem.tif')
if not os.path.exists(dem_file):
    print("DEM file not found. Run 01_gee_data_export.py first.")
    import sys
    sys.exit(1)

print("Starting Hydrological Processing...")

# 1. Fill depressions in DEM
filled_dem = os.path.join(out_dir, 'dem_filled.tif')
print("  Filling depressions...")
wbt.fill_depressions(dem_file, filled_dem)

# 2. D8 Flow Pointer
d8_pntr = os.path.join(out_dir, 'd8_pointer.tif')
print("  Calculating flow directions...")
wbt.d8_pointer(filled_dem, d8_pntr)

# 3. D8 Flow Accumulation
d8_accum = os.path.join(out_dir, 'd8_accum.tif')
print("  Calculating flow accumulation...")
wbt.d8_flow_accumulation(filled_dem, d8_accum)

# 4. Extract Streams (Threshold: e.g., > 1000 cells)
streams = os.path.join(out_dir, 'streams.tif')
print("  Extracting stream network...")
wbt.extract_streams(d8_accum, streams, threshold=1000.0)

# 5. Drainage Density (Optional advanced step - simplified proxy using focal sum)
# To keep it simple, we use a neighborhood analysis to find stream density
print("Calculating Drainage Density...")
drainage_density = os.path.join(out_dir, 'drainage_density.tif')
# Note: True drainage density requires stream length per area. 
# A proxy is the sum of stream pixels in a radius.
wbt.focal_sum(streams, drainage_density, filterx=51, filtery=51)

print("Hydrological processing complete! Drainage density proxy saved to:", drainage_density)
