import pandas as pd
import math
import time
import json
import tools
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
TAXES_DF = TAXES_DF[TAXES_DF['Closed Roll Fiscal Year'] == '2015']    
end = time.time()
print(end - start)

print("Loading Mappings")
start = time.time()
MAPPING = tools.load_parcel_map()
end = time.time()
print(end - start)

print("Preprocessing Lots...")
LOTS = {}
for index, row in tqdm(TAXES_DF.iterrows(), total=len(TAXES_DF)):

    #
    # Loading Parcel ID
    #

    parcelId = row['Block and Lot Number']
    if parcelId in MAPPING:
        parcelId = MAPPING[parcelId]

    # 
    # Creating record if not present
    #
    if parcelId not in LOTS:
        LOTS[parcelId] = {'extras': {}}

    #
    # Valuations
    #

    if isinstance(row['Closed Roll Assessed Land Value'], str):
        e = 0
        if 'land_value' in LOTS[parcelId]['extras']:
            e = LOTS[parcelId]['extras']['land_value']
        LOTS[parcelId]['extras']['land_value'] = int(row['Closed Roll Assessed Land Value']) + e
    if isinstance(row['Closed Roll Assessed Improvement Value'], str):
        e = 0
        if 'improvement_value' in LOTS[parcelId]['extras']:
            e = LOTS[parcelId]['extras']['improvement_value']
        LOTS[parcelId]['extras']['improvement_value'] = int(row['Closed Roll Assessed Improvement Value']) + e
    if isinstance(row['Closed Roll Assessed Fixtures Value'], str):
        e = 0
        if 'fixtures_value' in LOTS[parcelId]['extras']:
            e = LOTS[parcelId]['extras']['fixtures_value']
        LOTS[parcelId]['extras']['fixtures_value'] = int(row['Closed Roll Assessed Fixtures Value']) + e
    if isinstance(row['Closed Roll Assessed Personal Prop Value'], str):
        e = 0
        if 'personal_prop_value' in LOTS[parcelId]['extras']:
            e = LOTS[parcelId]['extras']['personal_prop_value']
        LOTS[parcelId]['extras']['personal_prop_value'] = int(row['Closed Roll Assessed Personal Prop Value']) + e

    #
    # Building Stats
    #

    if isinstance(row['Year Property Built'], str):
        LOTS[parcelId]['extras']['year_built'] = int(row['Year Property Built'])
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

    #
    # Some Random Dates
    #

    if isinstance(row['Current Sales Date'], str):
        LOTS[parcelId]['extras']['sales_date'] = pd.to_datetime(row['Current Sales Date']).strftime('%Y-%m-%d')
    if isinstance(row['Prior Sales Date'], str):
        LOTS[parcelId]['extras']['sales_date_prior'] = pd.to_datetime(row['Current Sales Date']).strftime('%Y-%m-%d')
    if isinstance(row['Recordation Date'], str):
        LOTS[parcelId]['extras']['recordation_date'] = pd.to_datetime(row['Recordation Date']).strftime('%Y-%m-%d')
        

save(LOTS, 'Taxes')