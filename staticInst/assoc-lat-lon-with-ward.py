import numpy as np 
import pandas as pd
import json 
import geopandas as gpd
from shapely.geometry import Point, MultiPolygon

blrDF = gpd.read_file("data/base/"+city+"/city.geojson")
blr_quarantined = pd.read_csv("data/base/"+city+"/BLR_incoming travel.csv")

ward = blrDF['wardNo'].values.tolist()
counts = [0]* len(ward)

cases_ln = blr_quarantined['lng'].values
cases_lt = blr_quarantined['lat'].values

def count_quarantineed(row, cases_ln, cases_lt, ward):
  for i in range(len(cases_ln)):
    point = Point(cases_ln[i], cases_lt[i])

    if MultiPolygon(row['geometry']).contains(point):
      counts[ward.index(row['wardNo'])] += 1  
  return counts

blrDF.apply(count_quarantineed, axis=1, args=(cases_ln, cases_lt, ward,))

quarantined = pd.DataFrame()
quarantined['wardNo'] = ward
quarantined['fracQuarantined'] = [value/sum(counts) for value in counts]
quarantined = quarantined.sort_values("wardNo")
quarantined.to_json("data/"+city+"/quarantinedPopulation.json", orient="records")

print(counts, sum(counts))
