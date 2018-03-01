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
from rtree import index

class Index:
    def __init__(self):
        self.index = index.Index()
        self.ids = {}
        self.ids_reverse = {}
        self.next_id = 0
    
    def insert(self, id, shp):
        if id not in self.ids:
            self.ids[id] = self.next_id
            self.ids_reverse[self.next_id] = id
            self.next_id = self.next_id + 1
        rid = self.ids[id]
        self.index.insert(rid, shape(shp).bounds)
    
    def inrersections(self, shp):
        ids =  self.index.intersection(shp.bounds)
        res = []
        for i in ids:
            res.append(self.ids_reverse[i])
        return res


def parse_polygon_coordinates(src):
    geometry = geojson.Feature(geometry=shapely.wkt.loads(src).simplify(0.00001, preserve_topology=True), properties={})
    return geometry.geometry['coordinates'][0]

def merge_polygon_coordinates(src):
    polygons = []
    for s in src:
        polygons.append([s])
    if len(polygons) == 0:
        return None
    if len(polygons) == 1:
        return geojson.Polygon(polygons[0])
    else:
        return geojson.MultiPolygon(polygons)

def save(src, name):
    f = open(name + ".jsvc","w")
    for k in src.keys():
        s = src[k]
        data = {}
        data['id'] = k
        for sk in s:
            if sk == 'geometry':
                data[sk] = s[sk].coordinates
            else:
                data[sk] = s[sk]
        # data['extras'] = convertExtras(s['extras'])
        # if 'blockId' in s:
        #    data['blockId'] = s['blockId']
        v = json.dumps(data)
        f.write(v + '\n')
    f.close()

def find_largest_inersection(geo, elements):
    max = -1
    id = None
    # try:
    gshape = shape(geo)
    for key in elements.keys():
        dst = shape(elements[key]['geometry'])
        area = dst.intersection(gshape).area
        if max < area:
            max = area
            id = key
    #except:
    #    pass
    return id

def find_largest_inersection_indexed(geo, elements, index: Index):
    max = -1
    id = None
    gshape = shape(geo)
    for key in index.inrersections(gshape):
        if key not in elements:
            continue
        dst = shape(elements[key]['geometry'])
        area = dst.intersection(gshape).area
        if max < area:
            max = area
            id = key
    return id

def load_parcel_map():
    mapping = pd.read_csv('Parcel_Mapping.csv', sep=',', dtype={ 'ParcelID': str, 'MapParcelID': str })
    res = {}
    for index, row in mapping.iterrows():
        mainParcelId = row['MapParcelID']
        parcelId = row['ParcelID']
        res[parcelId] = mainParcelId
    return res