import pandas as pd
import math
import time
import shapely.wkt
import geojson
import json
from shapely.geometry import shape
from shapely.ops import transform
import pyproj
from functools import partial
from tqdm import tqdm

print("Loading Blocks...")
start = time.time()
BLOCKS_DF = pd.read_csv("downloads/SF_Assesor_Blocks.csv", sep=',', dtype={
    'block_num': str,
    'geometry': str,
    'multigeom': bool,
})
end = time.time()
print(end - start)

print("Loading Lots...")
start = time.time()
LOTS_DF = pd.read_csv("downloads/SF_Assesor_Lots.csv", sep=',', dtype={
    'blklot': str,
    'block_num': str,
    'mapblklot': str,
    'geometry': str,
    'multigeom': bool,
})
end = time.time()
print(end - start)

print("Loading Districts...")
start = time.time()
SUPERVISOR_DF = pd.read_csv("downloads/SF_Supervisor_Districts.csv", sep=',', dtype={
    'supervisor': str,
    'the_geom': str,
})
ZONING_DF = pd.read_csv("downloads/SF_Parcels.csv", sep=',', dtype={
    'mapblklot': str,
    'zoning_sim': str,
})
end = time.time()
print(end - start)

def loadShape(src):
    geometry = geojson.Feature(geometry=src, properties={})
    return geometry.geometry

def findBestId(geo, df):
    max = -1
    id = None
    try:
        gshape = shape(geo)    
        for key in df.keys():
            dst = shape(df[key]['geometry'])
            area = dst.intersection(gshape).area
            if max < area:
                max = area
                id = key
    except:
        pass
    return id

def findAllIntersections(geo, df):
    res = []
    try:
        gshape = shape(geo)
        for key in df.keys():
            try:
                dst = shape(df[key]['geometry'])
                area = dst.intersection(gshape).area
                if area > 0:
                    res.append(df[key])
            except:
                pass
    except:
        pass        
    return res

def loadCoordinates(src):
    geometry = geojson.Feature(geometry=shapely.wkt.loads(src).simplify(0.00001, preserve_topology=True), properties={})
    return geometry.geometry['coordinates'][0]

def convertCoordinates(src):
    polygons = []
    for s in src:
        polygons.append([s])
    if len(polygons) == 0:
        return None
    if len(polygons) == 1:
        return geojson.Polygon(polygons[0])
    else:
        return geojson.MultiPolygon(polygons)

def convertExtras(src):
    res = {'ints':[], 'floats': [], 'strings': [], 'enums': []}
    for k in src.keys():
        s = src[k]
        if isinstance(s, str):
            res['strings'].append({'key': k, 'value': s})
        elif isinstance(s, float):
            res['floats'].append({'key': k, 'value': s})
        elif isinstance(s, int):
            res['ints'].append({'key': k, 'value': s})
        else:
            res['enums'].append({'key': k, 'value': s})
    return res


def measureArea(src):
    shp = shape(src)
    proj = partial(pyproj.transform, pyproj.Proj(init='epsg:4326'), pyproj.Proj(init='epsg:3857'))
    shpTransformed = transform(proj, shp)
    return shpTransformed.area

def save(src, name):
    f = open(name + ".jsvc","w")
    for k in src.keys():
        s = src[k]
        data = {}
        data['id'] = k
        data['geometry'] = s['geometry_raw']
        data['extras'] = convertExtras(s['extras'])
        if 'blockId' in s:
            data['blockId'] = s['blockId']
        v = json.dumps(data)
        f.write(v + '\n')
    f.close()

def saveGeoJson(src, name):
    features = []
    for k in src.keys():
        s = src[k]
        data = {}
        data['id'] = k
        for k2 in s.keys():
            if (k2 is not 'geometry_raw') and (k2 is not 'geometry'):
                data[k2] = s[k2]
        features.append(geojson.Feature(k, s['geometry'], data))
    data = json.dumps(geojson.FeatureCollection(features))
    f = open(name + ".geojson", "w")
    f.write(data)
    f.close()

#
# Preprocessing Districts
#

print("Preprocessing Districts...")
start = time.time()

SUPERVISOR={}
for intex, row in SUPERVISOR_DF.iterrows():
    district = row['supervisor']
    geo = shapely.wkt.loads(row['the_geom']).simplify(0.00001, preserve_topology=True)
    SUPERVISOR[district] = {
        'geometry': loadShape(geo)
    }

# ZONING={}
# for index, row in ZONING_DF.iterrows():
#     code = row['zoning_sim']
#     if code not in ZONING:
#         ZONING[code] = {'geometry_raw':[], 'extras': {}}
#     coordinates = loadCoordinates(row['geometry'])
#     ZONING[code]['geometry_raw'].append(coordinates)

# for key in ZONING.keys():
#     zone = ZONING[key]
#     geo_raw = zone['geometry_raw']
#     converted = convertCoordinates(geo_raw)
#     zone['geometry'] = converted
#     zone['extras']['area'] = measureArea(converted)


end = time.time()
print(end - start)    

#
# Preprocessing Blocks
#

print("Preprocessing Blocks...")
start = time.time()

BLOCKS = {}
for index, row in BLOCKS_DF.iterrows():
    block_number = row['block_num']
    if block_number not in BLOCKS:
        BLOCKS[block_number] = {'geometry_raw':[], 'extras': {}}
    if isinstance(row['geometry'], str):
        coordinates = loadCoordinates(row['geometry'])
        BLOCKS[block_number]['geometry_raw'].append(coordinates)

for key in BLOCKS.keys():
    block = BLOCKS[key]
    geo_raw = block['geometry_raw']
    converted = convertCoordinates(geo_raw)
    if converted is not None:    
        block['geometry'] = converted
        block['extras']['area'] = measureArea(converted)
        block['extras']['supervisor_id'] = findBestId(converted, SUPERVISOR)

end = time.time()
print(end - start)    

#
# Preprocessing Lots
#

print("Preprocessing Lots...")
start = time.time()

LOTS = {}
for index, row in tqdm(LOTS_DF.iterrows()):
    block_number = row['block_num']
    map_parcel = row['mapblklot']
    parcel = row['blklot']
    if map_parcel not in LOTS:
        LOTS[map_parcel] = {'geometry_raw':[], 'subparcels':[], 'extras': {'zoning':[]}}

    LOTS[map_parcel]['subparcels'].append(parcel)
    
    if (map_parcel == parcel) and isinstance(row['geometry'], str):
        coordinates = loadCoordinates(row['geometry'])
        LOTS[map_parcel]['geometry_raw'].append(coordinates)
        LOTS[map_parcel]['blockId'] = block_number

for key in tqdm(LOTS.keys()):
    block = LOTS[key]
    geo_raw = block['geometry_raw']
    converted = convertCoordinates(geo_raw)

    if converted is not None:
        block['geometry'] = converted
        block['extras']['area'] = measureArea(converted)
        block['extras']['supervisor_id'] = findBestId(converted, SUPERVISOR)

for index, row in ZONING_DF[ZONING_DF['zoning_sim'].notna()].iterrows():
    lot = row['mapblklot']
    zoning = row['zoning_sim']
    zoning_array = zoning.split('|')
    if lot in LOTS:
        lt = LOTS[lot]
        for z in zoning_array:
            if z not in lt['extras']['zoning']:
                lt['extras']['zoning'].append(z)

end = time.time()
print(end - start)

#
# Saving
#

saveGeoJson(SUPERVISOR, "Supervisor")
saveGeoJson(BLOCKS, "Blocks")

save(BLOCKS, "Blocks")
save(LOTS, "Lots")