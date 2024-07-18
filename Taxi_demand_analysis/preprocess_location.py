import pandas as pd
import numpy as np
import geopandas as gpd
from tqdm import tqdm
from glob import glob
import gc
import os



def count_locations(x):
    """
    Counts the number of locations in a given input that is a GeoPandas geometry
    
    Parameters
    ----------
    x: Geometry from a GeoPandas DataFrame
    returns the number of xy coordinates in the given data
    """
    loc = x

    # iterate through geometry and if has no geom method, then it's a Polygon
    # get the xy boundary if Polygon else get geoms of all polygons in multipolygon

    if not hasattr(loc, 'geoms'): # is a Polygon
        loc = list(loc.boundary.xy)
        loc = np.vstack(loc).T
        num_cities = len(loc)
        return(num_cities)
    elif hasattr(loc, 'geoms'): # is a MultiPolygon
        loc = list(loc.geoms)
        loc = list(map(lambda x: np.vstack(x.boundary.xy).T , loc))
        num_cities = sum(list(map(len, loc)))
        return (num_cities)



# get shapefile and taxi zone
path = os.getcwd()
taxi_shp = gpd.read_file(path+'/taxi_zones/taxi_zones.shp')
taxi_zone = pd.read_csv(path+'/taxi+_zone_lookup.csv')

# Projected polygon of imported shape file -> CRS: EPSG:2263

# converting to lower case
taxi_shp.columns = taxi_shp.columns.str.lower()
taxi_zone.columns = taxi_zone.columns.str.lower()


# converted from squared feet to squared km
# 1 sq.foot = 9.2903E-8
taxi_shp['area_km2'] = taxi_shp.area * 9.2903e-8
taxi_shp['length_km'] = taxi_shp.length * 0.0003048



# number of locations in coordinates
taxi_shp['n_cities'] = taxi_shp.geometry.apply(count_locations)




# get latitude and longitude of centriods (mean of coordinates)
taxi_shp['centroid']  = taxi_shp.centroid.to_crs(epsg=4326)
taxi_shp['longitude'] = taxi_shp['centroid'].x
taxi_shp['latitude'] = taxi_shp['centroid'].y


# location information
location_info = taxi_shp.groupby('locationid').agg(
    {
        'area_km2':'mean', 
        'length_km':'mean', 
        'latitude':'mean', 
        'longitude':'mean'
    }).reset_index()



location_info = location_info.merge(taxi_shp[['locationid', 'borough', 'zone', 'n_cities']], on='locationid')

cols_to_select = ['locationid', 'zone', 'borough', 'area_km2', 'length_km', 'n_cities', 'latitude', 'longitude']


location_info = location_info[cols_to_select].rename({'locationid':'ride_station'}, axis=1)
location_info.to_parquet('./location_info.parquet')
location_info.to_csv('./location_info.csv', index=False)


