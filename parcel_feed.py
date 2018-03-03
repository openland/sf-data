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
# Loading Dates
#

print('Loading Dates...')
dates = set()
for index, row in tqdm(LOTS_DF.iterrows(), total=len(LOTS_DF)):
    if isinstance(row['rec_add'], str):
        dates.add(row['rec_add'])
    if isinstance(row['rec_drop'], str):
        dates.add(row['rec_drop'])
dates = list(dates)
dates.sort(reverse=True)
dates = dates[:30]
# print(dates)

print('Building Feed')
events = {}
removed = {}
added = {}
for index, row in tqdm(LOTS_DF.iterrows(), total=len(LOTS_DF)):
    parcelId = row['blklot']

    drop_date = row['rec_drop']
    add_date = row['rec_add']
    
    drop_map_date = row['mad_drop']
    add_map_date = row['map_add']
    alter_map_date = row['map_alt']
    if isinstance(drop_date, str):
        if drop_date in dates:
            if drop_date not in removed:
                removed[drop_date]=[]
            if parcelId not in removed[drop_date]:
                removed[drop_date].append(parcelId)
    if isinstance(add_date, str):
        if add_date in dates: 
            if add_date not in added:
                added[add_date]=[]
            if parcelId not in added[add_date]:
                added[add_date].append(parcelId)

for date in dates:
    print('{}:'.format(date))
    if date in removed:
        for id in removed[date]:
            print('- {}'.format(id))
    if date in added:
        for id in added[date]:
            print('+ {}'.format(id))