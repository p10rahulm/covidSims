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

#Data-processing Functions
from modules.processDemographics import *
from modules.processGeoData import *

# Functions to instantiate individuals to houses, schools, workplaces and community centres
from modules.assignHouses import *
from modules.assignWorkplaces import *

#Global Variables from sys.argv


# get the city and target population as inputs
def instantiate(city, targetPopulation, averageStudents, averageWorkforce, averageHouseholds):
	targetPopulation = int(targetPopulation)
	averageHouseholds = float(averageHouseholds)
	averageStudents = float(averageStudents)
	averageWorkforce = float(averageWorkforce)

	#create directory to store parsed data
	if not os.path.exists("data/"+city):
		os.mkdir("data/"+city)   

	#TODO (SS):for the city get the base data (replace this with csv once Preetam gives data)
	print("processing data..")

	cityGeojson = "data/base/"+city+"/city.geojson"
	cityGeoDF = parse_geospatial_data(cityGeojson)

	if "cityProfile.json" not in os.listdir("data/base/"+city):
		cityDemographics = "data/base/"+city+"/demographics.json"
		cityHouseholds = "data/base/"+city+"/households.json"
		cityDemographicsDF = build_city_profile(cityGeoDF, cityDemographics, cityHouseholds)
	else:
		cityProfile = "data/base/"+city+"/cityProfile.json"
		ageDistribution, householdDistribution, schoolDistribution, cityDemographicsDF = process_city_profile(cityGeoDF, cityProfile)

	print("getting parameters ready ....") #create DataFrames
	cityDemographicsDF = project_population(cityDemographicsDF, targetPopulation) #scale population in city to the target population
	totalWorkingPopulation = (float(cityDemographicsDF[['age 20-24']].sum())*0.6)+\
													float(cityDemographicsDF[['age 30-34']].sum())+\
													float(cityDemographicsDF[['age 35-39']].sum())+\
													float(cityDemographicsDF[['age 40-44']].sum())+\
													float(cityDemographicsDF[['age 45-49']].sum())+\
													float(cityDemographicsDF[['age 50-54']].sum())+\
													float(cityDemographicsDF[['age 55-59']].sum())
	workplaceNeeded = int(totalWorkingPopulation/ averageWorkforce)
	
	totalStudents = (float(cityDemographicsDF[['age 0-4']].sum())*0.1)+\
													float(cityDemographicsDF[['age 5-9']].sum())+\
													float(cityDemographicsDF[['age 10-14']].sum())+\
													float(cityDemographicsDF[['age 15-19']].sum())+\
													float(cityDemographicsDF[['age 20-24']].sum()*0.3)
	schoolsNeeded = int(totalStudents/ averageStudents)

	totalNumberOfWards = len(cityDemographicsDF['wardNo'].values)

	commonArea = commonAreaLocation(cityGeoDF)
	schools = schoolLocation(cityGeoDF,  schoolsNeeded)
	workplaces = workplaceLocation(cityGeoDF,  workplaceNeeded)
	
	#assignment of individuals to households
	print("instantiating individuals and households...")
	individuals, households = assign_individuals_to_houses(targetPopulation, totalNumberOfWards, averageHouseholds, ageDistribution, householdDistribution)
	print("instantiating individual location by house...")
	households, individuals = houseLocation(cityDemographicsDF, individuals, households)

	print("instantiating individuals to workplaces and schools...")
	workplaces, schools, individuals = assign_schools_and_workplaces(cityDemographicsDF, workplaces, schools, individuals, schoolsNeeded, schoolDistribution)


	print("additonal data processing...")

	#associate individuals to common areas (by distance) and categorize workplace Type
	def getDistances(row, cc):
		findCommunityCentre = cc[int(row["wardNo"])]
		lat1 = row['lat']
		lon1 = row['lon']

		lat2 = findCommunityCentre[1]
		lon2 = findCommunityCentre[0]

		return distance(lat1, lon1, lat2, lon2)

	def getWorkplaceType(row):
		if not np.isnan(row['workplace']) and np.isnan(row['school']):
			return 1
		if np.isnan(row['workplace']) and not np.isnan(row['school']):
			return 2
		if np.isnan(row['workplace']) and np.isnan(row['school']):
			return 0

	individuals['CommunityCentreDistance'] = individuals.apply(getDistances, axis=1, args=(commonArea['location'].values,))
	individuals['workplaceType']=individuals.apply(getWorkplaceType, axis=1)

	#Combining the IDs for schools and workplaces
	schoolID = schools['ID'].values[-1]
	workplaceID = [schoolID+1 + index for index in workplaces['ID'].values]
	workplaces['ID'] = workplaceID
	workplaces = workplaces.sort_values(by=['ID'])

	print("saving instantiations as JSON....")
	workplaces = workplaces.sort_values("ID")
	schools = schools.sort_values("ID")
	individuals = individuals.sort_values("id")

	print(len(individuals), len(households), len(schools), len(workplaces), len(commonArea))
	individuals.to_json("data/"+city+"/individuals.json", orient='records')
	households[['id', 'wardNo' ,'lat', 'lon']].to_json("data/"+city+"/houses.json", orient='records')
	schools[['ID', 'ward' ,'lat', 'lon']].to_json("data/"+city+"/schools.json", orient='records')
	workplaces[['ID', 'ward' ,'lat', 'lon']].to_json("data/"+city+"/workplaces.json", orient='records')
	commonArea[['ID', 'wardNo' ,'lat', 'lon']].to_json("data/"+city+"/commonArea.json", orient='records')
	computeWardCentreDistance(cityGeoDF, "data/"+city+"/wardCentreDistance.json")

instantiate(city=sys.argv[1], targetPopulation=sys.argv[2], averageStudents=sys.argv[3], averageWorkforce=sys.argv[4], averageHouseholds=sys.argv[5])