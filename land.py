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

print("Loading Blocks...")
start = time.time()
BLOCKS_DF = pd.read_csv("downloads/SF_Assesor_Blocks.csv", sep=',', dtype={
    'block_num': str,
    'geometry': str,
    'multigeom': bool,
})
end = time.time()
print(end - start)

print("Loading Districts...")
start = time.time()
SUPERVISOR = pd.read_csv("downloads/SF_Supervisor_Districts.csv", sep=',', dtype={
    'supervisor': int,
    'the_geom': str,
})
end = time.time()
print(end - start)

def loadCoordinates(src):
    geometry = geojson.Feature(geometry=shapely.wkt.loads(src).simplify(0.00001, preserve_topology=True), properties={})
    return geometry.geometry['coordinates'][0]

def convertCoordinates(src):
    polygons = []
    for s in src:
        polygons.append([s])
    if len(polygons) == 1:
        return geojson.Polygon(polygons[0])
    else:
        return geojson.MultiPolygon(polygons)

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
        for k2 in s.keys():
            if k2 is not 'geometry_raw':
                data[k2] = s[k2]
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
# Preprocessing Blocks
#

BLOCKS = {}
for index, row in BLOCKS_DF.iterrows():
    block_number = row['block_num']
    coordinates = loadCoordinates(row['geometry'])
    if block_number not in BLOCKS:
        BLOCKS[block_number] = {'geometry_raw':[]}
    BLOCKS[block_number]['geometry_raw'].append(coordinates)

for key in BLOCKS.keys():
    block = BLOCKS[key]
    geo_raw = block['geometry_raw']
    converted = convertCoordinates(geo_raw)
    block['geometry'] = converted
    block['area'] = measureArea(converted)

save(BLOCKS, "Blocks")
saveGeoJson(BLOCKS, "Blocks")
