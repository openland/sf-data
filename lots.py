import pandas as pd
import math
import time
import shapely.wkt
import geojson
import json
from shapely.geometry import shape, Point
from shapely.ops import transform
import pyproj
from functools import partial
from tqdm import tqdm
import tools

print("Loading Lots...")
start = time.time()
LOTS_DF = pd.read_csv("downloads/SF_Parcels_History.csv", sep=',', dtype={
    'blklot': str,
    'block_num': str,
    'lot_num': str,
    'mapblklot': str,
    'mad_drop': str,
    'map_add': str,
    'map_alt': str,
    'rec_add': str,
    'rec_drop': str,
    'geometry': str,
    'multigeom': bool,
})
end = time.time()
print(end - start)

#
# Loading Geo
#

print("Loading all geometries")
PARCEL_GEO = {}
PARCEL_INDEX = tools.Index()
for index, row in tqdm(LOTS_DF.iterrows(), total=len(LOTS_DF)):
    parcelId = row['blklot']
    
    # Ignore All parcels without geometry
    if not isinstance(row['geometry'], str):
        continue
        
    # Create Default Instance if not present
    if parcelId not in PARCEL_GEO:
        PARCEL_GEO[parcelId] = []
        
    # Parsing Coordinates
    coordinates = tools.parse_polygon_coordinates(row['geometry'])
    PARCEL_GEO[parcelId].append(coordinates)

#
# Decode Geo
#
print("Decoding geometry")
for key in tqdm(PARCEL_GEO.keys()):

    # Decoding
    res = tools.merge_polygon_coordinates(PARCEL_GEO[key])
    PARCEL_GEO[key] = res

    # Indexing
    PARCEL_INDEX.insert(key, res)

#
# Loading Primary Parcels
#
print("Loading primary parcels")
PROCESSED = set()
PARCELS = {}
for index, row in tqdm(LOTS_DF.iterrows(), total=len(LOTS_DF)):
    mainParcelId = row['mapblklot']
    parcelId = row['blklot']

    # Skip all non-primary
    if mainParcelId != parcelId:
        continue
    
    # Skip all removed
    if isinstance(row['rec_drop'], str) or isinstance(row['mad_drop'], str):
        continue

    # Adding Geometry
    if mainParcelId in PARCEL_GEO:
        PARCELS[mainParcelId] = {'geometry': PARCEL_GEO[mainParcelId], 'related': []}
        PROCESSED.add(mainParcelId)


#
# Preprocess non-primary parcels
#
print('Loading secondary parcels')
for index, row in tqdm(LOTS_DF.iterrows(), total=len(LOTS_DF)):
    mainParcelId = row['mapblklot']
    parcelId = row['blklot']

    # Ignore processed
    if parcelId in PROCESSED:
        continue

    # Ignore primary lots
    if mainParcelId == parcelId:
        continue
    
    # Add direct parcel connection
    if mainParcelId in PARCELS:
        parcel = PARCELS[mainParcelId]
        if not parcelId in parcel['related']:
            parcel['related'].append(parcelId)
        PROCESSED.add(parcelId)

#
# Preprocessing remaining parcels
#
print('Loading remaining parcels')
for index, row in tqdm(LOTS_DF.iterrows(), total=len(LOTS_DF)):
    mainParcelId = row['mapblklot']
    parcelId = row['blklot']

    # Ignore processed
    if parcelId in PROCESSED:
        continue

    # Ignore the ones that doesn't have geometry
    if parcelId not in PARCEL_GEO:
        print('Warning: {}'.format(parcelId))
        continue
    
    intersection = tools.find_largest_inersection_indexed(PARCEL_GEO[parcelId], PARCELS, PARCEL_INDEX)
    if intersection is not None:
        primary = PARCELS[intersection]
        if not parcelId in primary['related']:
            primary['related'].append(parcelId)
        PROCESSED.add(parcelId)
    else:
        print('Warning (No intersection): {}'.format(parcelId))

#
# Saving
#
print('Saving')
tools.save(PARCELS, 'Parcels')

mapping = pd.DataFrame(columns=['ParcelID', 'MapParcelID'])
mapping = mapping.set_index('ParcelID')

for key in tqdm(PARCELS.keys()):
    for tkey in PARCELS[key]['related']:
        mapping = mapping.append({
            'ParcelID': tkey,
            'MapParcelID': key
        }, ignore_index=True)

mapping.to_csv('Parcel_Mapping.csv')

print('Done')