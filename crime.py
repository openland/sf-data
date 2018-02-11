import pandas as pd
import math
import time
import requests
import json

class InvalidResponseError(Exception):
    """Base class for exceptions in this module."""
    pass

session = requests.Session()

def upload_incidents(data):
    # initialized = getattr(SESSION_THREAD_LOCAL, 's', None)
    # if initialized is None:
    #     SESSION_THREAD_LOCAL.s = requests.Session()
    start = time.time()
    domain = "sf"
    staging_url = "https://statecraft-api-staging.herokuapp.com/api"
    production_url = "https://api.statecrafthq.com/api"
    local_url = "http://localhost:9000/api"
    local_docker_url = "http://docker.for.mac.localhost:9000/api"

    # if SERVER == "prod":
    #     url = production_url
    # elif SERVER == "staging":
    #     url = staging_url
    #     domain = "sfhousing"
    # elif SERVER == "docker":
    #     url = local_docker_url
    # else:
    url = production_url

    headers = {
        'x-statecraft-domain': domain,
        'Content-Type': 'application/json'
    }
    container = {
        "query":
        "mutation($data: [IncidentInput!]!) { updateIncidents(area: \"sf\", incidents: $data) }",
        "variables": {
            "data": data
        }
    }
    data = json.dumps(container)
    for i in range(3):
        response = session.post(url, data=data, headers=headers, stream=False)
        try:
            rdata = json.loads(response.text)
            if rdata['data']['updateIncidents'] != 'ok':
                raise InvalidResponseError("Wrong response!")
        except BaseException as e:
            print("Wrong Response!")
            print("Sent:")
            print(data)
            print("Got:")
            print(response.text)
            raise e

    #    print(r.text)
    end = time.time()
    return end - start

print("Loading Crime Dataset...")
start = time.time()
CRIMES = pd.read_csv(
    "downloads/SF_Crime.csv",
    sep=',',
    dtype={
        'PdId': str,
        'IncidntNum': str,
        'Date': str,
        'Time': str,
        # 'X': str,
        # 'Y': str
    })
end = time.time()
print(end - start)

category_map = {}
category_map['NON-CRIMINAL'] = 'NON_CRIMINAL'
category_map['ROBBERY'] = 'ROBBERY'
category_map['ASSAULT'] = 'ASSAULT'
category_map['SECONDARY CODES'] = 'SECONDARY_CODES'
category_map['VANDALISM'] = 'VANDALISM'
category_map['BURGLARY'] = 'BURGLARY'
category_map['LARCENY/THEFT'] = 'LARCENY'
category_map['DRUG/NARCOTIC'] = 'DRUG'
category_map['WARRANTS'] = 'WARRANTS'
category_map['VEHICLE THEFT'] = 'VEHICLE_THEFT'
category_map['ARSON'] = 'ARSON'
category_map['MISSING PERSON'] = 'MISSING_PERSON'

category_map['DRIVING UNDER THE INFLUENCE'] = 'DRIVING_UNDER_THE_INFLUENCE'
category_map['SUSPICIOUS OCC'] = 'SUSPICIOUS_OCC'
category_map['RECOVERED VEHICLE'] = 'RECOVERED_VEHICLE'
category_map['DRUNKENNESS'] = 'DRUNKENNESS'
category_map['TRESPASS'] = 'TRESPASS'

category_map['FRAUD'] = 'FRAUD'
category_map['DISORDERLY CONDUCT'] = 'DISORDERLY_CONDUCT'
category_map['SEX OFFENSES, FORCIBLE'] = 'SEX_OFFENSES_FORCIBLE'
category_map['FORGERY/COUNTERFEITING'] = 'COUNTERFEITING'
category_map['KIDNAPPING'] = 'KIDNAPPING'
category_map['EMBEZZLEMENT'] = 'EMBEZZLEMENT'
category_map['STOLEN PROPERTY'] = 'STOLEN_PROPERTY'
category_map['LIQUOR LAWS'] = 'LIQUOR_LAWS'
category_map['FAMILY OFFENSES'] = 'FAMILY_OFFENSES'
category_map['LOITERING'] = 'LOITERING'
category_map['BAD CHECKS'] = 'BAD_CHECKS'
category_map['TREA'] = 'TREA'
category_map['GAMBLING'] = 'GAMBLING'
category_map['RUNAWAY'] = 'RUNAWAY'
category_map['BRIBERY'] = 'BRIBERY'
category_map['PROSTITUTION'] = 'PROSTITUTION'
category_map['PORNOGRAPHY/OBSCENE MAT'] = 'PORNOGRAPHY'
category_map['SEX OFFENSES, NON FORCIBLE'] = 'SEX_OFFENSES_NON_FORCIBLE'
category_map['SUICIDE'] = 'SUICIDE'
category_map['EXTORTION'] = 'EXTORTION'
category_map['OTHER OFFENSES'] = 'OTHER_OFFENSES'
category_map['WEAPON LAWS'] = 'WEAPON_LAWS'

# 'NON-CRIMINAL' 'ROBBERY' 'ASSAULT' 'SECONDARY CODES' 'VANDALISM'
#  'BURGLARY' 'LARCENY/THEFT' 'DRUG/NARCOTIC' 'WARRANTS' 'VEHICLE THEFT'
#  'OTHER OFFENSES' 'WEAPON LAWS' 'ARSON' 'MISSING PERSON'
#  'DRIVING UNDER THE INFLUENCE' 'SUSPICIOUS OCC' 'RECOVERED VEHICLE'
#  'DRUNKENNESS' 'TRESPASS' 'FRAUD' 'DISORDERLY CONDUCT'
#  'SEX OFFENSES, FORCIBLE' 'FORGERY/COUNTERFEITING' 'KIDNAPPING'
#  'EMBEZZLEMENT' 'STOLEN PROPERTY' 'LIQUOR LAWS' 'FAMILY OFFENSES'
#  'LOITERING' 'BAD CHECKS' 'TREA' 'GAMBLING' 'RUNAWAY' 'BRIBERY'
#  'PROSTITUTION' 'PORNOGRAPHY/OBSCENE MAT' 'SEX OFFENSES, NON FORCIBLE'
#  'SUICIDE' 'EXTORTION'

data = []
for i in range(len(CRIMES)):
    d = CRIMES.iloc[i]
    data.append({
        'id': d['PdId'],
        'incidentNumber': d['IncidntNum'],
        'category': category_map[d['Category']],
        'location': {
            'latitude': d['Y'],
            'longitude': d['X']
        },
        'date': pd.to_datetime(d['Date'] + ' ' + d['Time']).strftime('%Y-%m-%d %H:%M:%S'),
        'description': d['Descript'],
        'resolution': d['Resolution'],
        'address': d['Address']
    })

    if len(data) > 200:
        start = time.time()
        upload_incidents(data)
        data = []
        end = time.time()
        print(end - start)

if len(data) > 200:
        upload_incidents(data)

# def converter(s):

#     if isinstance(s, str):
#         return s.split('|')[0].split(',')[0]
#     return 'None'
    

# PARCELS["districtna_converted"] = PARCELS["districtna"].apply(converter)
# PARCELS["zoning_sim_converted"] = PARCELS["zoning_sim"].apply(converter)

# print(PARCELS.groupby("districtna_converted").size())
# print(PARCELS["zoning_sim_converted"].unique())
# print(PARCELS.groupby("zoning_sim_converted").size())
# print(PARCELS[PARCELS["zoning_sim"] == "C-2|P"])