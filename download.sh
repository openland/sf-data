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