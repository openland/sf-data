import pandas as pd
import math
import time
print("Loading Parcels...")
start = time.time()
PARCELS = pd.read_csv(
    "downloads/Parcels.csv",
    sep=',',
    dtype={
        'blklot': str,
        'geometry': str,
        'block_num': str,
        'lot_num': str,
        'mapblklot': str,
        'datemap_dr': str
    })
end = time.time()
print(end - start)
def converter(s):
    if isinstance(s, str):
        return s.split('|')[0].split(',')[0]
    return 'None'
    

PARCELS["districtna_converted"] = PARCELS["districtna"].apply(converter)
PARCELS["zoning_sim_converted"] = PARCELS["zoning_sim"].apply(converter)

# print(PARCELS.groupby("districtna_converted").size())
# print(PARCELS["zoning_sim_converted"].unique())
# print(PARCELS.groupby("zoning_sim_converted").size())
print(PARCELS[PARCELS["zoning_sim"] == "C-2|P"])