import pandas as pd
import math
import time
print("Loading Parcels...")
start = time.time()
ZONING = pd.read_csv(
    "downloads/SF_Zoning.csv",
    sep=',',
    dtype={
        'districtna': str,
        'gen': str,
        'zoning': str,
        'zoning_sim': str,
        'url': str,
    })
ZONING=ZONING[["districtna", "gen", "zoning", "zoning_sim", "url"]]
ZONING=ZONING.drop_duplicates()
end = time.time()
print(end - start)
def converter(s):
    if isinstance(s, str):
        return s.split('|')[0].split(',')[0]
    return 'None'
    

# PARCELS["districtna_converted"] = PARCELS["districtna"].apply(converter)
# PARCELS["zoning_sim_converted"] = PARCELS["zoning_sim"].apply(converter)

# print(PARCELS.groupby("districtna_converted").size())
print(ZONING)

ZONING.to_csv('Zoning.csv')
# print(PARCELS.groupby("zoning_sim_converted").size())
# print(PARCELS[PARCELS["zoning_sim"] == "C-2|P"])