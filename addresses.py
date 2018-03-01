import pandas as pd
import math
import time
import json
from tqdm import tqdm
import tools

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


def save(src, name):
    f = open(name + ".jsvc","w")
    for k in src.keys():
        s = src[k]
        data = {}
        data['id'] = k
        data['extras'] = convertExtras(s['extras'])
        data['addresses'] = s['addresses']
        v = json.dumps(data)
        f.write(v + '\n')
    f.close()

print("Loading Addresses...")
start = time.time()
ADDRESSES_DF = pd.read_csv(
    "downloads/SF_Addresses_Full.csv",
    sep=',',
    dtype={
        'Block Lot': str
    })
end = time.time()
print(end - start)

# Lot Mappings

print("Lot Mappings")
start = time.time()
MAPPING = tools.load_parcel_map()
end = time.time()
print(end - start)

LOTS = {}
for index, row in tqdm(ADDRESSES_DF.iterrows(), total=len(ADDRESSES_DF)):
    parcelId = row['Block Lot']

    if not isinstance(parcelId, str):
        continue
    
    if parcelId in MAPPING:
        parcelId = MAPPING[parcelId]

    if parcelId not in LOTS:
        LOTS[parcelId] = {'extras': {},'addresses':[]}
    record = LOTS[parcelId]
    streetName = row['Street Name']
    streetNameSuffix = row['Street Type']
    streetNumber = row['Address Number']
    streetNumberSuffix = row['Address Number Suffix']
    if not isinstance(streetNumberSuffix, str):
        streetNumberSuffix = None
    if not isinstance(streetNameSuffix, str):
        streetNameSuffix = None
    
    if streetNameSuffix == 'AVE':
        streetNameSuffix = 'Av'
    if streetNameSuffix == 'WAY':
        streetNameSuffix = 'Wy'
    if streetNameSuffix == 'BLVD':
        streetNameSuffix = 'Bl'
    if streetNameSuffix == 'TER':
        streetNameSuffix = 'Tr'
    if streetNameSuffix == 'CIR':
        streetNameSuffix = 'Cr'
    if streetNameSuffix == 'HWY':
        streetNameSuffix = 'Hy'
    if streetNameSuffix == 'ALY':
        streetNameSuffix = 'Al'
    if streetNameSuffix == 'STWY':
        streetNameSuffix = 'Sw'
    if streetNameSuffix == 'PARK':
        streetNameSuffix = 'Pk'
    if streetNameSuffix == 'ROW':
        streetNameSuffix = 'Rw'
    if streetNameSuffix == 'PLZ':
        streetNameSuffix = 'Pl'
    if streetNameSuffix == 'LOOP':
        streetNameSuffix = 'Lp'
    if streetNameSuffix == 'WALK':
        streetNameSuffix = 'Wk'

    record['addresses'].append({
        'streetName': streetName,
        'streetNameSuffix': streetNameSuffix,
        'streetNumber': streetNumber,
        'streetNumberSuffix': streetNumberSuffix
    })

save(LOTS, 'Addresses')