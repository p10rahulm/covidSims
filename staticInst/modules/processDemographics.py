#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__name__ = "Module to process census demographic data"
___author__ = "Sharad"

import json
import numpy as np
import pandas as pd 

# if cleaned data for city demographics is available
def process_city_profile(geoDF, cityProFileFile):
    with open(cityProFileFile, "r") as jsonData:
        data = json.load(jsonData)
    
    age_distribution = data['age']['weights']
    household_distribution = data['householdSize']['weights']
    demographics = pd.read_json(json.dumps(data['demographics']))
    demographics = demographics.rename(columns={"Ward No.": "wardNo"})
    
    #add population density per ward
    demographics['Population Density'] = demographics.apply(lambda row: row['Total Population (in thousands)']/ row['Area (in sq km)'], axis=1)

    wardBounds = geoDF[['wardNo', 'wardBounds', 'wardCentre', 'neighbors']]
    demographics = pd.merge(demographics, wardBounds, on="wardNo", how="left")

    #Nidhin requested wards start from 0 to W-1
    demographics = demographics.reset_index()
    demographics = demographics.rename(columns={"index":"wardIndex"})

    #add average household size per ward
    demographics['Mean Household Size'] = demographics.apply(lambda row: row['Total Population (in thousands)']/ row['Total no. of Households'], axis = 1)

    del wardBounds, data
    
    return age_distribution, household_distribution ,demographics

# build demographic profile of the city and household data available per ward
def build_city_profile(geoDF, demographicDataFile, householdDataFile):
  with open(demographicDataFile, "r") as jsonData:
      data=json.load(jsonData)

  #Get the  column names
  colNames= []
  for field in data['fields']:
      colNames.append(field['label'])

  #Create a dataframe of the values
  demographics = pd.read_json(json.dumps(data['data']))

  #Refactoring Dataset
  demographics.rename(columns = dict(zip(demographics.columns, colNames)),inplace=True)
  demographics = demographics.drop(columns={'City Name', 'Zone Name','Population - Male (in thousands)', 'Population - female (in thousands)', 'population - children aged 0-14 (in thousands)', 'Population - youth aged 15-24 (in thousands)', 'Population - adults aged 25-60 (in thousands)', 'Population - Senior citizens aged 60+ (in thousands)'})
  demographics = demographics.rename(columns={"Ward No.": "wardNo"})

  #add population density per ward
  demographics['Population Density'] = demographics.apply(lambda row: row['Total Population (in thousands)']/ row['Area (in sq km)'], axis=1)

  wardBounds = geoDF[['wardNo', 'wardBounds']]
  demographics = pd.merge(demographics, wardBounds, on="wardNo", how="left")

  #Nidhin requested wards start from 0 to W-1
  demographics = demographics.reset_index()
  demographics = demographics.rename(columns={"index":"wardIndex"})

  with open(householdDataFile, "r") as jsonData:
      data = json.load(jsonData)

  #Get the  column names
  colNames= []
  for field in data['fields']:
      colNames.append(field['label'])

  #Create a dataframe of the values
  households = pd.read_json(json.dumps(data['data']))

  #Replace column indices with columnNames
  households.rename(columns = dict(zip(households.columns, colNames)),inplace=True)
  households = households.drop(columns=['City Name', 'Zone Name', 'Ward Name'])
  households = households.rename(columns={"Ward No.": "wardNo"})

  # #set Ward No. as index to the dataframe
  # households.set_index("Ward No.")

  #join households with demographics on Ward No.
  demographics = pd.merge(demographics, households, on="wardNo", how="left")

  #add average household size per ward
  demographics['Mean Household Size'] = demographics.apply(lambda row: row['Total Population (in thousands)']/ row['Total no. of Households'], axis = 1)
  del wardBounds, data, households
  
  return demographics


def project_population(demographics, targetPopulation):
    totalPopulation = sum(demographics['Total Population (in thousands)'].values)

    scalingFactor = targetPopulation/totalPopulation

    demographics['new Population'] = demographics.apply(lambda row: row['Total Population (in thousands)'] * scalingFactor, axis = 1)
    demographics['age 0-9'] = demographics.apply(lambda row: (row['new Population'] * 16.9)/100, axis = 1) #- This becomes gaps of 5 - use distribution in individual_assignment
    demographics['age 10-19'] = demographics.apply(lambda row: (row['new Population'] * 18.9)/100, axis = 1)
    demographics['age 20-29'] = demographics.apply(lambda row: (row['new Population'] * 19.3)/100, axis = 1)
    demographics['age 30-39'] = demographics.apply(lambda row: (row['new Population'] * 15.4)/100, axis = 1)
    demographics['age 40-49'] = demographics.apply(lambda row: (row['new Population'] * 12.1)/100, axis = 1)
    demographics['age 50-59'] = demographics.apply(lambda row: (row['new Population'] * 7.9)/100, axis = 1)
    demographics['age 60-69'] = demographics.apply(lambda row: (row['new Population'] * 5.9)/100, axis = 1)
    demographics['age 70-79'] = demographics.apply(lambda row: (row['new Population'] * 2.6)/100, axis = 1)
    demographics['age 80+'] = demographics.apply(lambda row: (row['new Population'] * 1)/100, axis = 1)

    #add scaled household size per ward - assuming the Mean Household size remains constant
    demographics['Scaled Number of Households'] = demographics.apply(lambda row: row['new Population']/ demographics['Mean Household Size'].describe()['mean'], axis = 1)
    demographics['Scaled Number of Households'] = demographics['Scaled Number of Households'].astype(int)

    return demographics