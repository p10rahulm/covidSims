#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright [2020] [Indian Institute of Science, Bangalore]
SPDX-License-Identifier: Apache-2.0
""" 
__name__ = "Module to process census demographic data"

import json
import numpy as np
import pandas as pd 

# if cleaned data for city demographics is available
def process_city_profile(geoDF, cityProFileFile):
    with open(cityProFileFile, "r") as jsonData:
        data = json.load(jsonData)
    
    age_distribution = data['age']['weights']
    household_distribution = data['householdSize']['weights']
    school_distribution = data['schoolsSize']['weights']
    demographics = pd.read_json(json.dumps(data['demographics']))
    # demographics = demographics.rename(columns={"Ward No.": "wardNo"})
    
    #add population density per ward
    demographics['Population Density'] = demographics.apply(lambda row: row['totalPopulation']/ row['area(sq km)'], axis=1)

    wardBounds = geoDF[['wardNo', 'wardBounds', 'wardCentre', 'neighbors']]
    demographics = pd.merge(demographics, wardBounds, on="wardNo", how="left")

    #Nidhin requested wards start from 0 to W-1
    demographics = demographics.reset_index()
    demographics = demographics.rename(columns={"index":"wardIndex"})

    #add average household size per ward
    demographics['Mean Household Size'] = demographics.apply(lambda row: row['totalPopulation']/ row['totalHouseholds'], axis = 1)

    del wardBounds, data
    demographics = demographics.sort_values("wardNo")
    return age_distribution, household_distribution, school_distribution, demographics

# build demographic profile of the city and household data available per ward [unprocessed Census Data]
# def build_city_profile(geoDF, demographicDataFile, householdDataFile):
#   with open(demographicDataFile, "r") as jsonData:
#       data=json.load(jsonData)

#   #Get the  column names
#   colNames= []
#   for field in data['fields']:
#       colNames.append(field['label'])

#   #Create a dataframe of the values
#   demographics = pd.read_json(json.dumps(data['data']))

#   #Refactoring Dataset
#   demographics.rename(columns = dict(zip(demographics.columns, colNames)),inplace=True)
#   demographics = demographics.drop(columns={'City Name', 'Zone Name','Population - Male (in thousands)', 'Population - female (in thousands)', 'population - children aged 0-14 (in thousands)', 'Population - youth aged 15-24 (in thousands)', 'Population - adults aged 25-60 (in thousands)', 'Population - Senior citizens aged 60+ (in thousands)'})
#   demographics = demographics.rename(columns={"Ward No.": "wardNo"})

#   #add population density per ward
#   demographics['Population Density'] = demographics.apply(lambda row: row['totalPopulation']/ row['area(sq km)'], axis=1)

#   wardBounds = geoDF[['wardNo', 'wardBounds']]
#   demographics = pd.merge(demographics, wardBounds, on="wardNo", how="left")

#   #Nidhin requested wards start from 0 to W-1
#   demographics = demographics.reset_index()
#   demographics = demographics.rename(columns={"index":"ward"}) #This would be the wardIndex

#   with open(householdDataFile, "r") as jsonData:
#       data = json.load(jsonData)

#   #Get the  column names
#   colNames= []
#   for field in data['fields']:
#       colNames.append(field['label'])

#   #Create a dataframe of the values
#   households = pd.read_json(json.dumps(data['data']))

#   #Replace column indices with columnNames
#   households.rename(columns = dict(zip(households.columns, colNames)),inplace=True)
#   households = households.drop(columns=['City Name', 'Zone Name', 'Ward Name'])
#   households = households.rename(columns={"Ward No.": "wardNo"})

#   # #set Ward No. as index to the dataframe
#   # households.set_index("Ward No.")

#   #join households with demographics on Ward No.
#   demographics = pd.merge(demographics, households, on="wardNo", how="left")

#   #add average household size per ward
#   demographics['Mean Household Size'] = demographics.apply(lambda row: row['totalPopulation']/ row['totalHouseholds'], axis = 1)
#   del wardBounds, data, households
  
#   return demographics


def project_population(demographics, targetPopulation):
    totalPopulation = sum(demographics['totalPopulation'].values)

    scalingFactor = targetPopulation/totalPopulation

    demographics['new Population'] = demographics.apply(lambda row: row['totalPopulation'] * scalingFactor, axis = 1)
    demographics['age 0-4'] = demographics.apply(lambda row: (row['new Population'] * 0.083), axis = 1) #- This becomes gaps of 5 - use distribution in individual_assignment
    demographics['age 5-9'] = demographics.apply(lambda row: (row['new Population'] * 0.086), axis = 1)
    demographics['age 10-14'] = demographics.apply(lambda row: (row['new Population'] * 0.094), axis = 1)
    demographics['age 15-19'] = demographics.apply(lambda row: (row['new Population'] * 0.095), axis = 1)
    demographics['age 20-24'] = demographics.apply(lambda row: (row['new Population'] * 0.099), axis = 1)
    demographics['age 25-29'] = demographics.apply(lambda row: (row['new Population'] * 0.094), axis = 1)
    demographics['age 30-34'] = demographics.apply(lambda row: (row['new Population'] * 0.077), axis = 1)
    demographics['age 35-39'] = demographics.apply(lambda row: (row['new Population'] * 0.077), axis = 1)
    demographics['age 40-44'] = demographics.apply(lambda row: (row['new Population'] * 0.063), axis = 1) #- This becomes gaps of 5 - use distribution in individual_assignment
    demographics['age 45-49'] = demographics.apply(lambda row: (row['new Population'] * 0.058), axis = 1)
    demographics['age 50-54'] = demographics.apply(lambda row: (row['new Population'] * 0.044), axis = 1)
    demographics['age 55-59'] = demographics.apply(lambda row: (row['new Population'] * 0.035), axis = 1)
    demographics['age 60-64'] = demographics.apply(lambda row: (row['new Population'] * 0.034), axis = 1)
    demographics['age 65-69'] = demographics.apply(lambda row: (row['new Population'] * 0.025), axis = 1)
    demographics['age 70-74'] = demographics.apply(lambda row: (row['new Population'] * 0.017), axis = 1)
    demographics['age 75-79'] = demographics.apply(lambda row: (row['new Population'] * 0.009), axis = 1)
    demographics['age 80+'] = demographics.apply(lambda row: (row['new Population'] * 0.01), axis = 1)


    #add scaled household size per ward - assuming the Mean Household size remains constant
    demographics['Scaled Number of Households'] = demographics.apply(lambda row: row['new Population']/ int(demographics['Mean Household Size'].describe()['mean']), axis = 1)
    demographics['Scaled Number of Households'] = demographics['Scaled Number of Households'].astype(int)

    return demographics