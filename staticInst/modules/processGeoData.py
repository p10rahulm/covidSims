#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright [2020] [Indian Institute of Science, Bangalore]
SPDX-License-Identifier: Apache-2.0
"""
__name__ = "Module to process geospatial data"
___author__ = "Sharad"

import numpy as np
import pandas as pd
import geopandas as gpd
from random import choice, uniform
from scipy.spatial.distance import pdist, squareform
from shapely.geometry import Point, MultiPolygon
import math

def polar_to_cartesian(row):
  R = 6371
  lat = row['lat']*np.pi/180
  lon = row['lon']*np.pi/180
  x = R*math.cos(lat)*math.cos(lon)
  y = R*math.cos(lat)*math.sin(lon)
  z = R*math.sin(lat)
  return x, y, z
#compute ward-centre distance matrix
def computeWardCentreDistance(geoDF, filepath):
  R = 6371
 
  ccMatrix = geoDF[['wardNo', 'wardCentre']]

  ccMatrix[['lon', 'lat']] = pd.DataFrame(ccMatrix['wardCentre'].tolist(), index=ccMatrix.index)
 
  ccMatrix['x'] = 0
  ccMatrix['y'] = 0
  ccMatrix['z'] = 0
  ccMatrix['x'] = ccMatrix.apply(polar_to_cartesian,axis = 1)
  ccMatrix[['x', 'y','z']] = pd.DataFrame(ccMatrix['x'].tolist(), index=ccMatrix.index)
 
  ccMatrix = ccMatrix.sort_values("wardNo")
  ccMatrix = pd.DataFrame(squareform(pdist(ccMatrix[['x', 'y','z']])), columns=ccMatrix.wardNo.unique(), index=ccMatrix.wardNo.unique())
  ccMatrix = ccMatrix.reset_index()
   
  ccMatrix = ccMatrix.rename(columns={"index":"ID"})
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
  cc['wardNo'] = geoDF['wardNo'].values
  cc['location'] = geoDF['wardCentre'].values
  cc['lat'] = cc.apply(lambda row: row['location'][1], axis=1)
  cc['lon'] = cc.apply(lambda row: row['location'][0], axis=1)
  cc = cc.sort_values(by=['wardNo']) #sort dataframe by wardNo
  cc = cc.reset_index()
  cc = cc.rename(columns={"index":"ID"})
  return cc

#assign houses across the wards randomly per ward
def houseLocation(geoDF, individuals, households):
  houseNumbers = individuals['household'].values

  # wardBounds = wardBounds.rename(columns={"wardNo": "Ward No"})
  wardBounds = geoDF[['wardNo', 'wardBounds']] #sorted by ward numbers
  households = pd.merge(households, wardBounds, on=['wardNo'])

  households['location'] = households.apply(lambda row: (np.random.choice([row['wardBounds'][0],row['wardBounds'][2]]), np.random.choice([row['wardBounds'][1], row['wardBounds'][3]])), axis=1)
  households['lat'] = households.apply(lambda row: row['location'][1], axis=1)
  households['lon'] = households.apply(lambda row: row['location'][0], axis=1)
  households['household'] = households['id'].values
  individuals = pd.merge(individuals, households[['household', 'wardNo', 'lat', 'lon']], on='household')
  individuals = individuals.sort_values(by=['id'])
  households = households.sort_values(by=['id'])
  return households, individuals


#assign location to schools per ward
def schoolLocation(geoDF, schoolsNeeded):
  schools = pd.DataFrame()
  wards = geoDF['wardNo'].values.tolist()
  bounds = geoDF['wardBounds'].values.tolist()

  ward = []
  lat = []
  lon = [] 
  loc = []
  for space in range(int(schoolsNeeded)):

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


  schools['ward'] = ward
  schools['lat'] = lat
  schools['lon'] = lon

  schools['location'] = loc
  schools = schools.reset_index()
  schools = schools.rename(columns={"index":"ID"})

  return schools


#assign location to workplaces
def workplaceLocation(geoDF, workplaceNeeded):
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

  return workplaces
