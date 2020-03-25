#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__name__ = "Module to process geospatial data"
___author__ = "Sharad"

import numpy as np
import pandas as pd
import geopandas as gpd
from random import choice, uniform
from scipy.spatial.distance import pdist, squareform
from shapely.geometry import Point, MultiPolygon

#return geojson
def getGeojson(geoDF, filepath):
  geoDF.to_file(filepath, driver='GeoJSON')

#compute ward-centre distance matrix
def computeWardCentreDistance(geoDF, filepath):
  ccMatrix = geoDF[['wardNo', 'wardCentre']]
  ccMatrix[['lon', 'lat']] = pd.DataFrame(ccMatrix['wardCentre'].tolist(), index=ccMatrix.index) 
  ccMatrix = pd.DataFrame(squareform(pdist(ccMatrix.iloc[:, 2:])), columns=ccMatrix.wardNo.unique(), index=ccMatrix.wardNo.unique())
  ccMatrix.to_json(filepath, orient="records")

#parsing geojson and using geometry of wards to compute ward centre and bounds
def parse_geospatial_data(geojsonFile):
  geoDF = gpd.read_file(geojsonFile)
  geoDF['wardNo'] = geoDF['wardNo'].astype(int)
  geoDF = geoDF[['wardNo', 'wardName', 'geometry']]
  geoDF['wardBounds'] = geoDF.apply(lambda row: MultiPolygon(row['geometry']).bounds, axis=1)
  geoDF['wardCentre'] = geoDF.apply(lambda row: (MultiPolygon(row['geometry']).centroid.x, MultiPolygon(row['geometry']).centroid.y), axis=1)
  geoDF["neighbors"] = geoDF.apply(lambda row: ", ".join([str(ward) for ward in geoDF[~geoDF.geometry.disjoint(row['geometry'])]['wardNo'].tolist() if row['wardNo'] != ward]) , axis=1)

  return geoDF[['wardNo', 'wardBounds', 'wardCentre', 'neighbors']]

#common areas are the ward centre
def commonAreaLocation(geoDF):
  cc = pd.DataFrame()
  cc['ward'] = geoDF['wardNo'].values
  cc['location'] = geoDF['wardCentre'].values
  cc['lat'] = cc.apply(lambda row: row['location'][1], axis=1)
  cc['lon'] = cc.apply(lambda row: row['location'][0], axis=1)
  cc = cc.sort_values(by=['ward']) #sort dataframe by wardNo
  return cc[['ward','lat', 'lon', 'location']]

#assign houses across the wards randomly per ward
def houseLocation(demographics, individuals, households):
  houseNumbers = individuals['household'].values
  #ward assignments based on ID column
  wardBounds = demographics.copy()
  wardBounds = wardBounds.rename(columns={"wardNo": "Ward No"})
  wardBounds = wardBounds[['Ward No', 'wardBounds']] #sorted by ward numbers
  households = pd.merge(households, wardBounds, on=['Ward No'])

  households['location'] = households.apply(lambda row: (np.random.choice([row['wardBounds'][0],row['wardBounds'][2]]), np.random.choice([row['wardBounds'][1], row['wardBounds'][3]])), axis=1)
  households['lat'] = households.apply(lambda row: row['location'][1], axis=1)
  households['lon'] = households.apply(lambda row: row['location'][0], axis=1)
  households['household'] = households['id'].values
  individuals = pd.merge(individuals, households[['household', 'Ward No', 'lat', 'lon']], on='household')
  individuals = individuals.rename(columns={"Ward No": "ward"})
  individuals = individuals.sort_values(by=['id'])
  households = households.sort_values(by=['id'])
  return households, individuals


#assign location to schools per ward
def schoolLocation(demographics, averageStudents):
  schools = pd.DataFrame()
  averageStudents = 300
  wards = demographics['wardNo'].values
  bounds = demographics['wardBounds'].values
  totalSchools = demographics.apply(lambda row: int(((row['age 0-4']*0.1) +\
                                                      row['age 5-9'] + \
                                                      row['age 10-14'] + \
                                                      row['age 15-19'] + \
                                                      (row['age 20-24']*0.3))/ averageStudents), axis=1) 

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
  return(schools)

#assign location to workplaces
def workplaceLocation(geoDF, schools, workplaceNeeded):
  workplaces = pd.DataFrame()
  wards = geoDF['wardNo'].values.tolist()
  bounds = geoDF['wardBounds'].values.tolist()

  ward = []
  lat = []
  lon = [] 
  loc = []
  for space in range(int(workplaceNeeded)):

      boundIndex = int(uniform(0, len(bounds)))

      lon1 = bounds[boundIndex][0]
      lat1 = bounds[boundIndex][1]
      lon2 = bounds[boundIndex][2]
      lat2 = bounds[boundIndex][3]

      ward.append(wards[boundIndex])
      ln = uniform(lon1, lon2)
      lt = uniform(lat1, lat2)
      lon.append(ln)
      lat.append(lt) 
      loc.append((ln, lt))


  workplaces['ward'] = ward
  workplaces['lat'] = lat
  workplaces['lon'] = lon

  workplaces['location'] = loc
  workplaces = workplaces.reset_index()
  workplaces = workplaces.rename(columns={"index":"ID"})


  #Combining the IDs for schools and workplaces
  schoolID = schools['ID'].values[-1]
  workplaceID = [schoolID+1 + index for index in workplaces['ID'].values]
  workplaces['ID'] = workplaceID
  workplaces = workplaces.sort_values(by=['ID'])

  return workplaces
