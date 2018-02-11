#!/bin/bash
set -e
rm -fr tmp
mkdir -p tmp
mkdir -p downloads

# Parcels
# shasum: 03095da0ed8eb047fc3bb008cac209974743e14f
wget -O "./tmp/SF_Parcels.csv" "https://storage.googleapis.com/datasets.statecraft.one/SF_Parcels_2017_05_10.csv"
mv ./tmp/SF_Parcels.csv ./downloads/SF_Parcels.csv

wget -O "./tmp/SF_Zoning.csv" "https://storage.googleapis.com/datasets.statecraft.one/SF_Zoning_2017_05_10.csv"
mv ./tmp/SF_Zoning.csv ./downloads/SF_Zoning.csv

wget -O "./tmp/SF_Crime.csv" "https://storage.googleapis.com/datasets.statecraft.one/SanFrancisco/SF_Crime_2018_02_05.csv"
mv ./tmp/SF_Crime.csv ./downloads/SF_Crime.csv

wget -O "./tmp/SF_Supervisor_Districts.csv" "https://storage.googleapis.com/datasets.statecraft.one/SanFrancisco/SF_Supervisor_Districts.csv"
mv ./tmp/SF_Supervisor_Districts.csv ./downloads/SF_Supervisor_Districts.csv

wget -O "./tmp/SF_Assesor_Tax.csv" "https://storage.googleapis.com/datasets.statecraft.one/SanFrancisco/SF_Assesor_Tax_2017_08_17.csv"
mv ./tmp/SF_Assesor_Tax.csv ./downloads/SF_Assesor_Tax.csv

wget -O "./tmp/SF_Assesor_Blocks.csv" "https://storage.googleapis.com/datasets.statecraft.one/SanFrancisco/SF_Assesor_Blocks_2018_02_10.csv"
mv ./tmp/SF_Assesor_Blocks.csv ./downloads/SF_Assesor_Blocks.csv

wget -O "./tmp/SF_Assesor_Lots.csv" "https://storage.googleapis.com/datasets.statecraft.one/SanFrancisco/SF_Assesor_Lots_2018_02_10.csv"
mv ./tmp/SF_Assesor_Lots.csv ./downloads/SF_Assesor_Lots.csv