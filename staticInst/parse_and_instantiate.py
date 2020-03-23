#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__name__ = "Instantiate a city and dump instantiations as json"
___author__ = "Sharad"

import os, sys
import json
import pandas as pd

#Data-processing Functions
from modules.processDemographics import *
from modules.processGeoData import *

# Functions to instantiate individuals to houses, schools, workplaces and community centres
from modules.assignHouses import *
from modules.assignWorkplaces import *

#Global Variables
city = "bangalore"
targetPopulation = 100000
averageStudents=300
averageWorkforce=20

# get the city and target population as inputs
def instantiate(city, targetPopulation, averageStudents, averageWorkforce):
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
		ageDistribution, householdDistribution, cityDemographicsDF = process_city_profile(cityGeoDF, cityProfile)

	cityDemographicsDF = project_population(cityDemographicsDF, targetPopulation) #scale population in city to the target population

	totalWorkingPopulation = (float(cityDemographicsDF[['age 20-29']].sum())*0.8)+\
													float(cityDemographicsDF[['age 30-39']].sum())+\
													float(cityDemographicsDF[['age 40-49']].sum())+\
													float(cityDemographicsDF[['age 50-59']].sum())

	workplaceNeeded = totalWorkingPopulation/ averageWorkforce

	print("getting parameters ready ....") #create DataFrames
	houses = houseLocation(cityDemographicsDF)
	schools = schoolLocation(cityDemographicsDF, averageStudents)
	workplaces = workplaceLocation(cityGeoDF, schools, workplaceNeeded)
	commonArea = commonAreaLocation(cityGeoDF)

	print("creating and populating virtual city..")
	totalNumberOfHouseholds = len(houses['ID'].values)
	totalNumberOfWards = len(cityDemographicsDF['wardNo'].values)

	#assignment of individuals to households
	individuals, householdsDF = assign_individuals_to_houses(targetPopulation, totalNumberOfWards, totalNumberOfHouseholds, ageDistribution, householdDistribution)
	individuals = assignLocation(individuals, houses['location'].values, houses['ward'].values)
	workplaces, schools, individuals = assign_schools_and_workplaces(cityDemographicsDF['neighbors'].values, workplaces, schools, individuals)
	#associate individuals to common areas (by distance) and categorize workplace Type
	def getDistances(row, cc):
		findCommunityCentre = cc[int(row["ward"])]
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

	print("saving instantiations as JSON....")
	individuals.to_json("data/"+city+"/individuals.json", orient='index')
	houses.to_json("data/"+city+"/houses.json", orient='index')
	schools.to_json("data/"+city+"/schools.json", orient='index')
	workplaces.to_json("data/"+city+"/workplaces.json", orient='index')
	commonArea.to_json("data/"+city+"/commonArea.json", orient='index')
	getGeojson(cityGeoDF, "data/"+city+"/map.geojson")

instantiate(city, targetPopulation, averageStudents, averageWorkforce)