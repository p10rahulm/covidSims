#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright [2020] [Indian Institute of Science, Bangalore]
SPDX-License-Identifier: Apache-2.0
"""
__name__ = "Instantiate a city and dump instantiations as json"

import os, sys
import json
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import time
import matplotlib.pyplot as plt

#Data-processing Functions
from modules.processDemographics import *
from modules.processGeoData import *

# Functions to instantiate individuals to houses, schools, workplaces and community centres
from modules.assignHouses import *
from modules.assignSchools import *
from modules.assignWorkplaces import *

# get the city and target population as inputs
def instantiate(city, targetPopulation, averageStudents, averageWorkforce):
	targetPopulation = int(targetPopulation)
	averageStudents = float(averageStudents)
	averageWorkforce = float(averageWorkforce)

	#create directory to store parsed data
	if not os.path.exists("data/"+city):
		os.mkdir("data/"+city)   
	
	print("processing data ready ...")
	start = time.time()
	cityGeojson = "data/base/"+city+"/city.geojson"
	cityGeoDF = parse_geospatial_data(cityGeojson)

	if "cityProfile.json" in os.listdir("data/base/"+city):
		cityProfile = "data/base/"+city+"/cityProfile.json"
		ageDistribution, householdDistribution, schoolDistribution, householdSizes, unemployed_fraction = process_city_profile(cityProfile)

	demographicsData = pd.read_csv("data/base/"+city+"/demographics.csv")
	housesData = pd.read_csv("data/base/"+city+"/households.csv")
	employmentData = pd.read_csv("data/base/"+city+"/employment.csv")
	print("processing data completed completed in ", time.time() - start)
	

	print("getting parameters ready ...")
	start = time.time()
	demographicsData = process_data(demographicsData, housesData, employmentData, targetPopulation, ageDistribution) 

	totalPopulation = demographicsData['totalPopulation'].values.sum()
	if unemployed_fraction == 0:
		people_over_60 = float(demographicsData[['age 60-64']].sum()) + float(demographicsData[['age 65-69']].sum()) + float(demographicsData[['age 70-74']].sum()) + float(demographicsData[['age 75-79']].sum()) + float(demographicsData[['age 80+']].sum())

		population_over_60 = totalPopulation * (people_over_60/ totalPopulation)
		total_employable = (float(demographicsData[['age 15-19']].sum())+\
														float(demographicsData[['age 20-24']].sum()))+\
														float(demographicsData[['age 25-29']].sum())+\
														float(demographicsData[['age 30-34']].sum())+\
														float(demographicsData[['age 35-39']].sum())+\
														float(demographicsData[['age 40-44']].sum())+\
														float(demographicsData[['age 45-49']].sum())+\
														float(demographicsData[['age 50-54']].sum())+\
														float(demographicsData[['age 55-59']].sum())

		employable_population = totalPopulation * ((total_employable/totalPopulation)) + ((float(demographicsData[['age 15-19']].sum())/totalPopulation) * 0.5)

		total_unemployed = demographicsData['unemployed'].values.sum()
		unemployed_but_employable = total_unemployed - population_over_60
		unemployed_fraction = unemployed_but_employable  / (totalPopulation - population_over_60)

	# print(people_over_60, unemployed_fraction, employable_population, total_employable, total_unemployed, unemployed_but_employable )

	totalNumberOfWards = len(demographicsData['wardNo'].values)
	averageHouseholds = totalPopulation / demographicsData['totalHouseholds'].values.sum()

	commonArea = commonAreaLocation(cityGeoDF)
	print("getting parameters ready completed in ", time.time() - start)

	#assignment of individuals to households
	print("instantiating individuals to households...")
	start = time.time()
	print("computed unemployment fraction = ", unemployed_fraction)
	individuals, households = assign_individuals_to_houses(targetPopulation, totalNumberOfWards, ageDistribution, householdSizes, householdDistribution, unemployed_fraction)
	print("instantiating individuals to households completed in ", time.time() - start)
	
	print("instantiating individual location by house location...")
	start = time.time()
	households, individuals = houseLocation(cityGeoDF, individuals, households)
	print("instantiating individual location by house location completed in ", time.time() - start)

	print("instantiating individuals to workplaces...")
	start = time.time()
	workplaces, individuals = assign_workplaces(cityGeoDF, individuals)
	print("instantiating individuals to workplaces completed in ", time.time() - start)

	print("instantiating individuals to schools...")
	start = time.time()
	individuals, schools = assign_schools(individuals, cityGeoDF,  schoolDistribution)
	print("instantiating individuals to schools completed in ", time.time() - start)

	print("additonal data processing...")
	start = time.time()
	#associate individuals to common areas (by distance) and categorize workplace Type
	def getDistances(row, cc):
		findCommunityCentre = cc[int(row["wardIndex"])]
		lat1 = row['lat']
		lon1 = row['lon']

		lat2 = findCommunityCentre[1]
		lon2 = findCommunityCentre[0]

		return distance(lat1, lon1, lat2, lon2)

	individuals['CommunityCentreDistance'] = individuals.apply(getDistances, axis=1, args=(commonArea['location'].values.tolist(),))

	#Combining the IDs for schools and workplaces
	schoolID = schools['ID'].values[-1]
	workplaceID = [schoolID+1 + index for index in workplaces['ID'].values]
	workplaces['ID'] = workplaceID
	workplaces = workplaces.sort_values(by=['ID'])

	demographicsData['fracPopulation'] = demographicsData.apply(lambda row: row['totalPopulation']/demographicsData['totalPopulation'].values.sum(), axis=1)

	print("additonal data processing completed in ", time.time() - start)

	print("saving instantiations as JSON....")
	start = time.time()
	individuals.to_json("data/"+city+"/individuals.json", orient='records')
	households[['id', 'wardNo' ,'lat', 'lon']].to_json("data/"+city+"/houses.json", orient='records')
	schools[['ID', 'ward' ,'lat', 'lon']].to_json("data/"+city+"/schools.json", orient='records')
	workplaces[['ID', 'ward' ,'lat', 'lon']].to_json("data/"+city+"/workplaces.json", orient='records')
	commonArea[['ID', 'wardNo' ,'lat', 'lon']].to_json("data/"+city+"/commonArea.json", orient='records')
	computeWardCentreDistance(cityGeoDF, "data/"+city+"/wardCentreDistance.json")
	demographicsData[['wardNo', 'totalPopulation', 'fracPopulation']].to_json("data/"+city+"/fractionPopulation.json", orient="records")
	print("saving instantiations as JSON completed in ", time.time() - start)

	
instantiate(city=sys.argv[1], targetPopulation=sys.argv[2], averageStudents=sys.argv[3], averageWorkforce=sys.argv[4])