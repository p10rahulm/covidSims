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
def process_city_profile(cityProFileFile):
    with open(cityProFileFile, "r") as jsonData:
        data = json.load(jsonData)
    
    age_distribution = data['age']['weights']
    household_distribution = data['householdSize']['weights']
    school_distribution = data['schoolsSize']['weights']

    return age_distribution, household_distribution, school_distribution

def process_data(demographics, households, employmentData, targetPopulation, age_distribution):
    households = households.sort_values('Ward No.')
    employmentData = employmentData.sort_values('Ward No.')
    age_distribution = [float(value) for value in age_distribution]
    

    demographics['totalHouseholds'] = households['Total no. of Households'].values
    demographics['employed'] = employmentData['No. of employed persons'].values
    demographics['unemployed'] = employmentData['No. of unemployed persons (seeking or available for work)'].values

    demographics['Total Population (in thousands)'] = demographics.apply(lambda row: row['population - children aged 0-14 (in thousands)']+ row['employed'] + row['unemployed'], axis=1)
    
    demographics['Mean Household Size'] = demographics.apply(lambda row: row['Total Population (in thousands)']/ row['totalHouseholds'], axis = 1)
    
    totalPopulation = demographics['Total Population (in thousands)'].values.sum()

    demographics = demographics.drop(columns={'City Name', 'Zone Name','Population - Male (in thousands)', 'Population - female (in thousands)',  'Population - youth aged 15-24 (in thousands)', 'Population - adults aged 25-60 (in thousands)', 'Population - Senior citizens aged 60+ (in thousands)'})
    
    demographics['age 0-4'] = demographics.apply(lambda row: (row['population - children aged 0-14 (in thousands)'] * age_distribution[0]), axis = 1) 
    demographics['age 5-9'] = demographics.apply(lambda row: (row['population - children aged 0-14 (in thousands)'] * age_distribution[1]), axis = 1)
    demographics['age 10-14'] = demographics.apply(lambda row: (row['population - children aged 0-14 (in thousands)'] * age_distribution[2]), axis = 1)
    demographics['age 15-19'] = demographics.apply(lambda row: (row['Total Population (in thousands)'] * age_distribution[3]), axis = 1)
    demographics['age 20-24'] = demographics.apply(lambda row: (row['Total Population (in thousands)'] * age_distribution[4]), axis = 1)
    demographics['age 25-29'] = demographics.apply(lambda row: (row['Total Population (in thousands)'] * age_distribution[5]), axis = 1)
    demographics['age 30-34'] = demographics.apply(lambda row: (row['Total Population (in thousands)'] * age_distribution[6]), axis = 1)
    demographics['age 35-39'] = demographics.apply(lambda row: (row['Total Population (in thousands)'] * age_distribution[7]), axis = 1)
    demographics['age 40-44'] = demographics.apply(lambda row: (row['Total Population (in thousands)'] * age_distribution[8]), axis = 1) 
    demographics['age 45-49'] = demographics.apply(lambda row: (row['Total Population (in thousands)'] * age_distribution[9]), axis = 1)
    demographics['age 50-54'] = demographics.apply(lambda row: (row['Total Population (in thousands)'] * age_distribution[10]), axis = 1)
    demographics['age 55-59'] = demographics.apply(lambda row: (row['Total Population (in thousands)'] * age_distribution[11]), axis = 1)
    demographics['age 60-64'] = demographics.apply(lambda row: (row['Total Population (in thousands)'] * age_distribution[12]), axis = 1)
    demographics['age 65-69'] = demographics.apply(lambda row: (row['Total Population (in thousands)'] * age_distribution[13]), axis = 1)
    demographics['age 70-74'] = demographics.apply(lambda row: (row['Total Population (in thousands)'] * age_distribution[14]), axis = 1)
    demographics['age 75-79'] = demographics.apply(lambda row: (row['Total Population (in thousands)'] * age_distribution[15]), axis = 1)
    demographics['age 80+'] = demographics.apply(lambda row: (row['Total Population (in thousands)'] * age_distribution[16]), axis = 1)

    return demographics