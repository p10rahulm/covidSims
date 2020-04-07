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
	#create directory to store parsed data
	path = "data/%s_population%s_students%s"%(city, targetPopulation, averageStudents)
	if not os.path.exists(path):
		os.mkdir(path)   

	targetPopulation = int(targetPopulation)
	averageStudents = int(averageStudents)
	averageWorkforce = float(averageWorkforce)

	print("processing data ready ...")
	start = time.time()
	cityGeojson = "data/base/"+city+"/city.geojson"
	cityGeoDF = parse_geospatial_data(cityGeojson)

	if "cityProfile.json" in os.listdir("data/base/"+city):
		cityProfile = "data/base/"+city+"/cityProfile.json"
		ageDistribution, householdDistribution, schoolDistribution, householdSizes, maxWorkplaceDistance = process_city_profile(cityProfile)

	demographicsData = pd.read_csv("data/base/"+city+"/demographics.csv")
	housesData = pd.read_csv("data/base/"+city+"/households.csv")
	employmentData = pd.read_csv("data/base/"+city+"/employment.csv")
	print("processing data completed completed in ", time.time() - start)
	

	print("getting parameters ready ...")
	start = time.time()
	demographicsData = process_data(demographicsData, housesData, employmentData, targetPopulation, ageDistribution) 

	totalPopulation = demographicsData['totalPopulation'].values.sum()

	unemployed_fraction = demographicsData['unemployed'].values.sum()  / (demographicsData['employed'].values.sum() + demographicsData['unemployed'].values.sum())

	totalNumberOfWards = len(demographicsData['wardNo'].values)
	averageHouseholds = totalPopulation / demographicsData['totalHouseholds'].values.sum()

	commonArea = commonAreaLocation(cityGeoDF)
	print("getting parameters ready completed in ", time.time() - start)

	#assignment of individuals to households
	print("instantiating individuals to households...")
	start = time.time()
	print("computed unemployment fraction = ", unemployed_fraction)
	households, individuals = assign_individuals_to_houses(targetPopulation, totalNumberOfWards, ageDistribution, householdSizes, householdDistribution, unemployed_fraction)
	print("instantiating individuals to households completed in ", time.time() - start)
	
	print("instantiating individual location by house location...")
	start = time.time()
	households, individuals = houseLocation(cityGeoDF, individuals, households)
	print("instantiating individual location by house location completed in ", time.time() - start)

	individuals = individuals.sort_values("id")
	individuals = individuals.drop_duplicates()
	households = households.sort_values("id")

	individuals.to_json(path+"/individuals.json", orient='records')
	households[['id', 'wardNo' ,'lat', 'lon']].to_json(path+"/houses.json", orient='records')
	exit()

	#split the individuals by workplace type
	individuals = {name: individuals.loc[individuals['workplaceType'] == name, :] for name in individuals['workplaceType'].unique()}
	
	print("instantiating individuals to workplaces...")
	start = time.time()
	workplaces, individuals[1] = assign_workplaces(cityGeoDF, individuals[1], maxWorkplaceDistance)
	print("instantiating individuals to workplaces completed in ", time.time() - start)
	
	
	print("instantiating individuals to schools...")
	start = time.time()
	individuals[2], schools = assign_schools(individuals[2], cityGeoDF,  schoolDistribution)
	print("instantiating individuals to schools completed in ", time.time() - start)
	
	
	#join the individuals
	individuals = pd.concat(individuals.values(), ignore_index=True)
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


	#Combining the IDs for schools and workplaces
	schoolID = schools['ID'].values[-1]
	workplaceID = [schoolID+1 + index for index in workplaces['ID'].values]
	workplaces['ID'] = workplaceID
	

	individuals = individuals.sort_values("id")
	households = households.sort_values("id")
	workplaces = workplaces.sort_values("ID")
	schools = schools.sort_values("ID")
	commonArea = commonArea.sort_values("ID")
	
	demographicsData['fracPopulation'] = demographicsData.apply(lambda row: row['totalPopulation']/demographicsData['totalPopulation'].values.sum(), axis=1)

	print("additonal data processing completed in ", time.time() - start)
	flag = (len(np.where(pd.isnull(individuals.loc[individuals['workplaceType']<0.5,'school'])==False)[0])==0 and \
	len(np.where(pd.isnull(individuals.loc[individuals['workplaceType']<0.5,'workplace'])==False)[0])==0 and \
	len(np.where(pd.isnull(individuals.loc[individuals['workplaceType']>1.5,'workplace'])==False)[0])==0 and \
	len(np.where(pd.isnull(individuals.loc[individuals['workplaceType']<1.5,'school'])==False)[0])==0 and \
	len(np.where(pd.isnull(individuals.loc[individuals['workplaceType']>1.5,'school'])==True)[0])==0 and \
	len(np.where(pd.isnull(individuals.loc[individuals['workplaceType']==1,'workplace'])==True)[0])==0)

	print((len(individuals) == int(targetPopulation)))
	if(flag) and (len(individuals) == int(targetPopulation)):
		print("saving instantiations as JSON....")
		start = time.time()
		individuals.to_json(path+"/individuals.json", orient='records')
		households[['id', 'wardNo' ,'lat', 'lon']].to_json(path+"/houses.json", orient='records')
		schools[['ID', 'ward' ,'lat', 'lon']].to_json(path+"/schools.json", orient='records')
		workplaces[['ID', 'ward' ,'lat', 'lon']].to_json(path+"/workplaces.json", orient='records')
		commonArea[['ID', 'wardNo' ,'lat', 'lon']].to_json(path+"/commonArea.json", orient='records')
		computeWardCentreDistance(cityGeoDF, path+"/wardCentreDistance.json")
		demographicsData[['wardNo', 'totalPopulation', 'fracPopulation']].to_json(path+"/fractionPopulation.json", orient="records")
		print("saving instantiations as JSON completed in ", time.time() - start)
	else:
		print("instantiation failed, please re-run")
	
instantiate(city=sys.argv[1], targetPopulation=sys.argv[2], averageStudents=sys.argv[3], averageWorkforce=sys.argv[4])