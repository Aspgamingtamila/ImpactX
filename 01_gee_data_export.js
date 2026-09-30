// ==============================================================================
// 01_gee_data_export.js
// Copy and paste this code into the Google Earth Engine Web Code Editor
// (https://code.earthengine.google.com/) and click "Run".
// Then go to the "Tasks" tab to run the exports to your Google Drive.
// ==============================================================================

// 1. Define Study Area (Darjeeling)
var districts = ee.FeatureCollection("FAO/GAUL/2015/level2");
var darjeeling = districts.filter(ee.Filter.eq('ADM2_NAME', 'Darjiling'));
var roi = darjeeling.geometry();

Map.centerObject(roi, 10);
Map.addLayer(roi, {color: 'red'}, 'Darjeeling Boundary', false);

var years = [2011, 2015, 2025];

// 2. Topography (DEM, Slope, Aspect)
var dem = ee.Image("NASA/NASADEM_HGT/001").select('elevation').clip(roi);
var slope = ee.Terrain.slope(dem);
var aspect = ee.Terrain.aspect(dem);

Map.addLayer(slope, {min: 0, max: 60, palette: ['green', 'yellow', 'red']}, 'Slope', false);

Export.image.toDrive({
  image: dem, description: 'Darjeeling_DEM', scale: 30, region: roi, maxPixels: 1e10
});
Export.image.toDrive({
  image: slope, description: 'Darjeeling_Slope', scale: 30, region: roi, maxPixels: 1e10
});
Export.image.toDrive({
  image: aspect, description: 'Darjeeling_Aspect', scale: 30, region: roi, maxPixels: 1e10
});

// 3. Rainfall (CHIRPS - Monsoon Totals)
var chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY");

years.forEach(function(year) {
  var startDate = year + '-06-01';
  var endDate = year + '-09-30';
  
  var monsoon_rain = chirps.filterDate(startDate, endDate).sum().clip(roi);
  
  Export.image.toDrive({
    image: monsoon_rain, 
    description: 'Darjeeling_Rainfall_' + year, 
    scale: 5566, 
    region: roi, 
    maxPixels: 1e10
  });
});

// 4. NDVI (Landsat 7 for 2011, Sentinel-2 for 2015 & 2025)
years.forEach(function(year) {
  var ndvi;
  
  if (year < 2015) {
    // Landsat 7
    var l7 = ee.ImageCollection("LANDSAT/LE07/C02/T1_L2")
      .filterBounds(roi)
      .filterDate(year + '-01-01', year + '-12-31')
      .filter(ee.Filter.lt('CLOUD_COVER', 20))
      .median()
      .clip(roi);
    ndvi = l7.normalizedDifference(['SR_B4', 'SR_B3']).rename('NDVI');
  } else {
    // Sentinel-2
    var s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
      .filterBounds(roi)
      .filterDate(year + '-01-01', year + '-12-31')
      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
      .median()
      .clip(roi);
    ndvi = s2.normalizedDifference(['B8', 'B4']).rename('NDVI');
  }
  
  Export.image.toDrive({
    image: ndvi, 
    description: 'Darjeeling_NDVI_' + year, 
    scale: 30, 
    region: roi, 
    maxPixels: 1e10
  });
});

// 5. Land Cover (ESA WorldCover 2021)
var worldcover = ee.ImageCollection("ESA/WorldCover/v200").first().clip(roi);
Map.addLayer(worldcover, {}, 'Land Cover', false);

Export.image.toDrive({
  image: worldcover, 
  description: 'Darjeeling_Landcover', 
  scale: 10, 
  region: roi, 
  maxPixels: 1e10
});

print("Run the exports in the 'Tasks' tab on the right to save files to your Google Drive.");
