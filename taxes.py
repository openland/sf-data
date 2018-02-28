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
        'Year Property Built': str,
        'Number of Bathrooms': str,
        'Number of Bedrooms': str,
        'Number of Rooms': str,
        'Number of Stories': str,
        'Number of Units': str,
        'Current Sales Date': str,
        'Prior Sales Date': str,
        'Recordation Date': str
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
    if isinstance(row['Number of Bathrooms'], str):
        LOTS[parcelId]['extras']['count_bathrooms'] = int(float(row['Number of Bathrooms']))
    if isinstance(row['Number of Bedrooms'], str):
        LOTS[parcelId]['extras']['count_bedrooms'] = int(float(row['Number of Bedrooms']))
    if isinstance(row['Number of Rooms'], str):
        LOTS[parcelId]['extras']['count_rooms'] = int(float(row['Number of Rooms']))
    if isinstance(row['Number of Stories'], str):
        LOTS[parcelId]['extras']['count_stories'] = int(float(row['Number of Stories']))
    if isinstance(row['Number of Units'], str):
        LOTS[parcelId]['extras']['count_units'] = int(float(row['Number of Units']))

    if isinstance(row['Current Sales Date'], str):
        LOTS[parcelId]['extras']['sales_date'] = pd.to_datetime(row['Current Sales Date']).strftime('%Y-%m-%d')
    if isinstance(row['Prior Sales Date'], str):
        LOTS[parcelId]['extras']['sales_date_prior'] = pd.to_datetime(row['Current Sales Date']).strftime('%Y-%m-%d')
    if isinstance(row['Recordation Date'], str):
        LOTS[parcelId]['extras']['recordation_date'] = pd.to_datetime(row['Recordation Date']).strftime('%Y-%m-%d')
        

save(LOTS, 'Taxes')