import pandas as pd
import math
import time
import json
from tqdm import tqdm

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
        # 'Closed Roll Fiscal Year': str,
        # 'Block and Lot Number': str,
        # 'Closed Roll Assessed Fixtures Value': str,
        # 'Closed Roll Assessed Land Value': str,
        # 'Closed Roll Assessed Personal Prop Value': str,
        # 'Closed Roll Assessed Improvement Value': str,
        # 'Year Property Built': str
    })
end = time.time()
print(end - start)


print(ADDRESSES_DF['Street Type'].unique())
# TAXES_DF = TAXES_DF[TAXES_DF['Closed Roll Fiscal Year'] == '2015']

# print("Preprocessing Lots...")
# start = time.time()

LOTS = {}
for index, row in tqdm(ADDRESSES_DF.iterrows()):
    parcelId = row['Block Lot']
    if not isinstance(parcelId, str):
        continue
    
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

# 'St' | 'Av' | 'Dr' | 'Bl' | 'Wy' | 'Ln' | 'Hy' | 'Tr' | 'Pl' | 'Ct' |
#    'Pk' | 'Al' | 'Cr' | 'Rd' | 'Sq' | 'Pz' | 'Sw' | 'No' | 'Rw' | 'So' | 'Hl' | 'Wk'
#     row['']

#     if isinstance(row['Closed Roll Assessed Land Value'], str):
#         LOTS[parcelId]['extras']['land_value'] = row['Closed Roll Assessed Land Value']
#     if isinstance(row['Closed Roll Assessed Improvement Value'], str):
#         LOTS[parcelId]['extras']['improvement_value'] = row['Closed Roll Assessed Improvement Value']
#     if isinstance(row['Closed Roll Assessed Fixtures Value'], str):
#         LOTS[parcelId]['extras']['fixtures_value'] = row['Closed Roll Assessed Fixtures Value']
#     if isinstance(row['Closed Roll Assessed Personal Prop Value'], str):
#         LOTS[parcelId]['extras']['personal_prop_value'] = row['Closed Roll Assessed Personal Prop Value']

#     if isinstance(row['Year Property Built'], str):
#         LOTS[parcelId]['extras']['year_built'] = row['Year Property Built']


save(LOTS, 'Addresses')