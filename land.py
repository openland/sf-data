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

CALTRAIN = [
    {'name': 'San Francisco 4th & King St.', 'location': [37.776389, -122.394444]},
    {'name': '22nd St.', 'location': [37.757222, -122.3925]},
    {'name': 'Bayshore ','location': [37.7075, -122.401944]}
]

BART = [
    {'name': '16th St. Mission', 'location': [37.764847, -122.420042]},
    {'name': '24th St. Mission', 'location': [37.752, -122.4187]},
    {'name': 'Balboa Park', 'location': [37.721629, -122.447519]},
    {'name': 'Civic Center/UN Plaza', 'location': [37.779861, -122.413498]},
    {'name': 'Embarcadero', 'location': [37.793056, -122.397222]},
    {'name': 'Montgomery St.', 'location': [37.789355, -122.401942]},
    {'name': 'Powell St.', 'location': [37.784, -122.408]},
    {'name': 'San Francisco International Airport', 'location': [37.6164, -122.391]}
]

MUNI = [
    {'name': 'San Francisco 4th & King St.', 'location': [37.776389, -122.394444]},
    {'name': 'Balboa Park', 'location': [37.721629, -122.447519]},
    {'name': 'Civic Center/UN Plaza', 'location': [37.779861, -122.413498]},
    {'name': 'Embarcadero', 'location': [37.793056, -122.397222]},
    {'name': 'Montgomery St.', 'location': [37.789355, -122.401942]},
    {'name': 'Powell St.', 'location': [37.784, -122.408]},
    {'name': 'Ocean Beach', 'location': [37.76028, -122.50913]},
    {'name': 'Judah & Sunset', 'location': [37.76087, -122.49568]},
    {'name': 'Judah & 19th Avenue', 'location': [37.7617, -122.47703]},
    {'name': 'Judah & 9th Avenue', 'location': [37.76218, -122.46618]},
    {'name': 'UCSF Parnassus', 'location': [37.763250, -122.458278]},
    {'name': 'Carl & Cole', 'location': [37.76578, -122.44997]},
    {'name': 'Duboce & Noe', 'location': [37.76919, -122.43357]},
    {'name': 'Duboce & Church', 'location': [37.76946, -122.42912]},
    {'name': 'Van Ness', 'location': [37.775, -122.419]},
    {'name': 'Folsom', 'location': [37.79045, -122.38954]},
    {'name': 'Brannan', 'location': [37.784367, -122.388147]},
    {'name': '2nd & King', 'location': [37.77942, -122.3901]},
    {'name': 'SF Zoo', 'location': [37.73618, -122.50421]},
    {'name': 'Taraval & Sunset', 'location': [37.74222, -122.49438]},
    {'name': 'Taraval & 22nd Avenue', 'location': [37.74291, -122.47891]},
    {'name': 'West Portal', 'location': [37.740908, -122.465994]},
    {'name': 'Forest Hill', 'location': [37.74803, -122.45914]},
    {'name': 'Castro', 'location': [37.76252, -122.43553]},
    {'name': 'Church', 'location': [37.767814, -122.429067]},
    {'name': 'Sunnydale', 'location': [37.70881, -122.4052]},
    {'name': 'Arleta', 'location': [37.71245, -122.40254]},
    {'name': 'Le Conte', 'location': [37.718819, -122.397481]},
    {'name': 'Gilman/Paul', 'location': [37.722411, -122.395624]},
    {'name': 'Carroll', 'location': [37.725636, -122.394186]},
    {'name': 'Williams', 'location': [37.72925, -122.39257]},
    {'name': 'Revere/Shafter', 'location': [37.732294, -122.391494]},
    {'name': 'Oakdale/Palou', 'location': [37.734314, -122.390861]},
    {'name': 'Kirkwood/La Salle', 'location': [37.737559, -122.389766]},
    {'name': 'Hudson/Innes', 'location': [37.739962, -122.388921]},
    {'name': 'Evans', 'location': [37.7428, -122.3879]},
    {'name': 'Marin St.', 'location': [37.748992, -122.387439]},
    {'name': '23rd St.', 'location': [37.7558, -122.3882]},
    {'name': '20th St.', 'location': [37.76036, -122.38855]},
    {'name': 'Mariposa', 'location': [37.764, -122.3884]},
    {'name': 'UCSF Mission Bay Station', 'location': [37.768823, -122.389289]},
    {'name': 'Mission Rock', 'location': [37.772964, -122.389672]},
    {'name': 'Church & 18th St.', 'location': [37.7613, -122.42838]},
    {'name': 'Church & 24th St.', 'location': [37.7517, -122.42743]},
    {'name': 'Church & 30th St.', 'location': [37.74233, -122.42262]},
    {'name': 'San Jose & Randall', 'location': [37.73986, -122.42426]},
    {'name': 'San Jose & Geneva', 'location': [37.720730, -122.446630]},
    {'name': 'Broad & Plymouth', 'location': [37.71318, -122.45608]},
    {'name': 'Randolph & Arch', 'location': [37.71426, -122.4671]},
    {'name': 'Stonestown', 'location': [37.727222, -122.474722]},
    {'name': 'SF State', 'location': [37.721667, -122.475139]},
    {'name': 'St. Francis Circle', 'location': [37.73476, -122.47009]},
    {'name': 'Junipero Serra & Ocean', 'location': [37.73116, -122.47214]},
    {'name': 'Ocean & Jules', 'location': [37.72495, -122.46123]},
    {'name': 'Ocean & Lee', 'location': [37.72349, -122.4541]},
    {'name': 'City College', 'location': [37.725716, -122.450178]}
]

ZONING_RESIDENTAL = ['RH-1', 'RH-2', 'RH-3', 'RH-1(D)', 'RH-1(S)', 'RM-4', 'RM-1', 'RM-2', 'RM-3', 'RTO', 'RTO-M', 'PM-R', 'RED', 'RH DTR', 'TB DTR', 'SB-DTR', '']
ZONING_MIXRES = ['NCT', 'RC-4', 'RC-3', 'NC-1', 'NC-S', 'NC-2', 'NC-3', 'PM-MU1', 'PM-MU2', 'WMUG', 'NCD', 'NCT', 'MUG', 'MUR', 'NCT-1', 'NCT-2', 'MUO', 'WMUO', 'CRNC', 'UMU', 'RED-MX', 'SPD', 'NCT-3', 'HP-RA', 'MB-RA',
            'NCT-VALENCIA', 'NCT-24TH-MISSION', 'NCD-24TH-NOE-VALLEY', 'NCD-WEST PORTAL', 'NCD-PACIFIC', 'NCD-INNER SUNSET', 'NCT-UPPER MARKET', 'NCT-SOMA', 'NCT-MISSION', 'NCT-GLEN PARK', 'NCT-OCEAN', 
            'NCT-FILLMORE', 'NCD-IRVING', 'NCT-FOLSOM', 'NCD-TARAVAL', 'NCD-JUDAH', 'NCD-EXCELSIOR', 'NCD-BROADWAY', 'NCD-CASTRO', 'NCT-DIVISADERO', 'NCD-JAPANTOWN', 'NCD-INNER CLEMENT', 'NCD-OUTER CLEMENT', 'NCD-UPPER FILLMORE',
            'NCT-HAYES', 'NCD-HAIGHT', 'NCD-UPPER MARKET', 'NCD-NORTH BEACH', 'NCD-POLK', 'NCD-SACRAMENTO', 'NCD-UNION', 'NCD-NORIEGA']
ZONING_INDUSTRIAL = ['PDR-1-D', 'PDR-1-G', 'PDR-1-B', 'M-1', 'M-2', 'PDR-2', 'SALI', 'SLI']
ZONING_PUBLIC = ['P', 'MB-OS', 'PM-CF', 'PM-OS', 'PM-S']
ZONING_COMMERCIAl = ['C-2', 'C-3-G', 'C-3-S', 'C-3-O', 'C-3-O(SD)', 'C-3-R', 'RCD', 'CCB', 'CVR', 'MB-O', 'SSO']

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
# LOTS_DF = pd.read_csv("downloads/SF_Parcels.csv", sep=',', dtype={
#     'blklot': str,
#     'block_num': str,
#     'mapblklot': str,
#     'geometry': str,
#     'multigeom': bool,
# })
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
    'zoning_sim': str
})
NEIGHBOURHOODS_DF = pd.read_csv("downloads/SF_Realtor_Neighborhoods.csv", sep=',', dtype={
    'nbrhood': str,
    'the_geom': str,
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

def findNearest(geo, df):
    min = 10000000000
    res = None
    try:
        gshape = shape(geo)    
        for key in range(len(df)):
            # print(key)
            src = df[key]
            distance = measureDistance(gshape,  src['location'])
            if min > distance:
                min = distance
                res = src
    except:
        pass
    return {'distance': min, 'station': res}

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

def measureDistance(src, point):
    proj = partial(pyproj.transform, pyproj.Proj(init='epsg:4326'), pyproj.Proj(init='epsg:3857'))
    srcTransformed = transform(proj, src)
    pointTransformed = transform(proj, Point(point[1],point[0]))
    return pointTransformed.distance(srcTransformed)

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

NEIGHBOURHOODS={}
for intex, row in NEIGHBOURHOODS_DF.iterrows():
    district = row['nbrhood']
    geo = shapely.wkt.loads(row['the_geom']).simplify(0.00001, preserve_topology=True)
    NEIGHBOURHOODS[district] = {
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

        station = findNearest(converted, MUNI)
        block['extras']['nearest_muni'] = station['station']['name']
        block['extras']['nearest_muni_distance'] = station['distance']
        block['extras']['nearest_muni_location'] = station['station']['location']

        station = findNearest(converted, CALTRAIN)
        block['extras']['nearest_caltrain'] = station['station']['name']
        block['extras']['nearest_caltrain_distance'] = station['distance']
        block['extras']['nearest_caltrain_location'] = station['station']['location']

        station = findNearest(converted, BART)
        block['extras']['nearest_bart'] = station['station']['name']
        block['extras']['nearest_bart_distance'] = station['distance']
        block['extras']['nearest_bart_location'] = station['station']['location']
        # block['extras']['supervisor_id'] = findBestId(converted, SUPERVISOR)
        # block['extras']['neighbourhoods'] = findBestId(converted, NEIGHBOURHOODS)

end = time.time()
print(end - start)    

#
# Preprocessing Lots
#

print("Preprocessing Lots...")
start = time.time()

LOTS = {}
for index, row in tqdm(LOTS_DF.iterrows(), total=len(LOTS_DF)):
    block_number = row['block_num']
    map_parcel = row['mapblklot']
    parcel = row['blklot']
    if map_parcel not in LOTS:
        LOTS[map_parcel] = {'geometry_raw':[], 'subparcels':[], 'extras': {'zoning':[],'land_use':[]}}

    LOTS[map_parcel]['subparcels'].append(parcel)
    
    if (map_parcel == parcel) and isinstance(row['geometry'], str):
        coordinates = loadCoordinates(row['geometry'])
        LOTS[map_parcel]['geometry_raw'].append(coordinates)
        LOTS[map_parcel]['blockId'] = block_number

for key in tqdm(LOTS.keys(), total=len(LOTS)):
    block = LOTS[key]
    geo_raw = block['geometry_raw']
    converted = convertCoordinates(geo_raw)

    if converted is not None:
        block['geometry'] = converted
        block['extras']['area'] = measureArea(converted)
        block['extras']['supervisor_id'] = findBestId(converted, SUPERVISOR)
        block['extras']['neighbourhoods'] = findBestId(converted, NEIGHBOURHOODS)

        station = findNearest(converted, MUNI)
        block['extras']['nearest_muni'] = station['station']['name']
        block['extras']['nearest_muni_distance'] = station['distance']
        block['extras']['nearest_muni_location'] = station['station']['location']

        station = findNearest(converted, CALTRAIN)
        block['extras']['nearest_caltrain'] = station['station']['name']
        block['extras']['nearest_caltrain_distance'] = station['distance']
        block['extras']['nearest_caltrain_location'] = station['station']['location']

        station = findNearest(converted, BART)
        block['extras']['nearest_bart'] = station['station']['name']
        block['extras']['nearest_bart_distance'] = station['distance']
        block['extras']['nearest_bart_location'] = station['station']['location']

for index, row in ZONING_DF[ZONING_DF['zoning'].notna()].iterrows():
    lot = row['mapblklot']
    zoning = row['zoning']
    zoning_array = zoning.split('|')
    zoning_cat = []
    for z in zoning_array:
        if z in ZONING_RESIDENTAL:
            if 'Residental' not in zoning_cat:
                zoning_cat.append('Residental')
        elif z in ZONING_PUBLIC:
            if 'Public' not in zoning_cat:
                zoning_cat.append('Public')
        elif z in ZONING_MIXRES:
            if 'Mixed Use' not in zoning_cat:
                zoning_cat.append('Mixed Use')
        elif z in ZONING_INDUSTRIAL:
            if 'Industrial' not in zoning_cat:
                zoning_cat.append('Industrial')
        elif z in ZONING_COMMERCIAl:
            if 'Commercial' not in zoning_cat:
                zoning_cat.append('Commercial')
        else:
            print('Missing {}'.format(z))

    if lot in LOTS:
        lt = LOTS[lot]
        for z in zoning_array:
            if z not in lt['extras']['zoning']:
                lt['extras']['zoning'].append(z)
        for z in zoning_cat:
            if z not in lt['extras']['land_use']:
                 lt['extras']['land_use'].append(z)
        
        # print(row['gen'])
        # land_use = row['gen']
        # if land_use not in lt['extras']['land_use']:
        #     lt['extras']['land_use'].append(land_use)

end = time.time()
print(end - start)

#
# Saving
#

# saveGeoJson(SUPERVISOR, "Supervisor")
# saveGeoJson(BLOCKS, "Blocks")

save(BLOCKS, "Blocks")
save(LOTS, "Lots")