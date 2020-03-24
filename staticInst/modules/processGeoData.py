#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__name__ = "Module to process geospatial data"
___author__ = "Sharad"

import numpy as np
import pandas as pd
import geopandas as gpd
from random import choice, uniform
from shapely.geometry import Point, MultiPolygon

#return geojson
def getGeojson(geoDF, filepath):
  geoDF.to_file(filepath, driver='GeoJSON')

#parsing geojson and using geometry of wards to compute ward centre and bounds
def parse_geospatial_data(geojsonFile):
  geoDF = gpd.read_file(geojsonFile)
  geoDF['WARD_NO'] = geoDF['WARD_NO'].astype(int)
  geoDF = geoDF[['WARD_NO', 'WARD_NAME', 'geometry']]
  geoDF = geoDF.rename(columns={"WARD_NO": "wardNo"})
  geoDF['wardBounds'] = geoDF.apply(lambda row: MultiPolygon(row['geometry']).bounds, axis=1)
  geoDF['wardCentre'] = geoDF.apply(lambda row: (MultiPolygon(row['geometry']).centroid.x, MultiPolygon(row['geometry']).centroid.y), axis=1)
  geoDF["neighbors"] = geoDF.apply(lambda row: ", ".join([str(ward) for ward in geoDF[~geoDF.geometry.disjoint(row['geometry'])]['wardNo'].tolist() if row['wardNo'] != ward]) , axis=1)

  return geoDF 

#common areas are the ward centre
def commonAreaLocation(geoDF):
  cc = pd.DataFrame()
  cc['wardNo'] = geoDF['wardNo'].values
  cc['location'] = geoDF['wardCentre'].values
  cc = cc.sort_values(by=['wardNo']) #sort dataframe by wardNo
  return cc

#assign houses across the wards randomly per ward
def houseLocation(demographics):
  houses = pd.DataFrame()
  wards = demographics['wardNo'].values
  bounds = demographics['wardBounds'].values
  households = demographics['Scaled Number of Households'].values

  ward = []
  location = []

  for i in range(len(wards)):
    lon1 = bounds[i][0]
    lat1 = bounds[i][1]
    lon2 = bounds[i][2]
    lat2 = bounds[i][3]

    for house in range(households[i]):
      ward.append(i+1)
      location.append((uniform(lon1, lon2), uniform(lat1, lat2)))
  
  houses['ward'] = ward
  houses['location'] = location
  houses = houses.reset_index()
  houses = houses.rename(columns={"index":"ID"})
  return houses


#assign location to schools per ward
def schoolLocation(demographics, averageStudents):
  schools = pd.DataFrame()

  wards = demographics['wardNo'].values
  bounds = demographics['wardBounds'].values
  totalSchools = demographics.apply(lambda row: int(((row['age 0-9']*0.6) + (row['age 20-29']*0.2) + row['age 10-19'])/ averageStudents), axis=1) 

  ward = []
  location = []

  for i in range(len(wards)):
    lon1 = bounds[i][0]
    lat1 = bounds[i][1]
    lon2 = bounds[i][2]
    lat2 = bounds[i][3]

    for house in range(totalSchools[i]):
      ward.append(i+1)
      location.append((uniform(lon1, lon2), uniform(lat1, lat2)))
  
  schools['ward'] = ward
  schools['location'] = location
  schools = schools.reset_index()
  schools = schools.rename(columns={"index":"ID"})
  return schools

#assign location to workplaces
def workplaceLocation(geoDF, schools, workplaceNeeded):
  ward = []
  location = []
  workplaces = pd.DataFrame()

  wards = geoDF['wardNo'].values
  wards = [value-1 for value in wards]
  bounds = geoDF['wardBounds'].values

  for space in range(int(workplaceNeeded)):

    boundIndex = int(uniform(0, len(bounds)))
        
    lon1 = bounds[boundIndex][0]
    lat1 = bounds[boundIndex][1]
    lon2 = bounds[boundIndex][2]
    lat2 = bounds[boundIndex][3]

    ward.append(wards[boundIndex])
    location.append((uniform(lon1, lon2), uniform(lat1, lat2)))

      

  workplaces['ward'] = 0
  workplaces['location'] = 0
  workplaces = workplaces.reset_index()
  workplaces = workplaces.rename(columns={"index":"ID"})

  #Combining the IDs for schools and workplaces
  schoolID = schools['ID'].values
  workplaceID = [schoolID[-1]+1 + index for index in workplaces['ID'].values]
  workplaces['ID'] = workplaceID

  return workplaces

#add lat and lon for an individual
def assignLocation(individuals, houseLocList, houseWardList):
  lat = []
  lon = []
  ward = []

  houseAssigned = individuals['household'].values
  for house in houseAssigned:
    pos = houseLocList[house]
    lat.append(pos[1])
    lon.append(pos[0])
    ward.append(houseWardList[house])
  
  individuals['lat'] = lat
  individuals['lon'] = lon
  individuals['ward'] = ward

  return individuals
