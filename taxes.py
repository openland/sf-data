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
        v = json.dumps(data)
        f.write(v + '\n')
    f.close()

print("Loading Taxes...")
start = time.time()
TAXES_DF = pd.read_csv(
    "downloads/SF_Assesor_Tax.csv",
    sep=',',
    dtype={
        'Closed Roll Fiscal Year': str,
        'Block and Lot Number': str,
        'Closed Roll Assessed Fixtures Value': str,
        'Closed Roll Assessed Land Value': str,
        'Closed Roll Assessed Personal Prop Value': str,
        'Closed Roll Assessed Improvement Value': str,
        'Year Property Built': str
    })
end = time.time()
print(end - start)

TAXES_DF = TAXES_DF[TAXES_DF['Closed Roll Fiscal Year'] == '2015']

print("Preprocessing Lots...")
start = time.time()

LOTS = {}
for index, row in tqdm(TAXES_DF.iterrows()):
    parcelId = row['Block and Lot Number']
    if parcelId not in LOTS:
        LOTS[parcelId] = {'extras': {}}

    if isinstance(row['Closed Roll Assessed Land Value'], str):
        LOTS[parcelId]['extras']['land_value'] = row['Closed Roll Assessed Land Value']
    if isinstance(row['Closed Roll Assessed Improvement Value'], str):
        LOTS[parcelId]['extras']['improvement_value'] = row['Closed Roll Assessed Improvement Value']
    if isinstance(row['Closed Roll Assessed Fixtures Value'], str):
        LOTS[parcelId]['extras']['fixtures_value'] = row['Closed Roll Assessed Fixtures Value']
    if isinstance(row['Closed Roll Assessed Personal Prop Value'], str):
        LOTS[parcelId]['extras']['personal_prop_value'] = row['Closed Roll Assessed Personal Prop Value']

    if isinstance(row['Year Property Built'], str):
        LOTS[parcelId]['extras']['year_built'] = row['Year Property Built']


save(LOTS, 'Taxes')