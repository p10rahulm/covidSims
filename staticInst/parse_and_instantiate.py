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
	individuals = individuals.drop_duplicates()

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
	
	#associate individuals to common areas (by distance) 
	def getDistances(row, cc):
		houseNo = row['household']
		lat1 = row['lat']
		lon1 = row['lon']
		# lat1 = households.loc[households['id']==houseNo, 'lat'].values[0]
		# lon1 = households.loc[households['id']==houseNo, 'lon'].values[0]
		
		assignedWard = row["wardNo"]
		lat2 = cc.loc[cc['wardNo']==assignedWard, 'lat'].values[0]
		lon2 = cc.loc[cc['wardNo']==assignedWard, 'lon'].values[0]
		
		return distance(lat1, lon1, lat2, lon2)


	#Combining the IDs for schools and workplaces
	schoolID = schools['ID'].values[-1]
	workplaceID = [schoolID+1 + index for index in workplaces['ID'].values]
	workplaces['ID'] = workplaceID
	

	individuals = individuals.sort_values("id")
	households = households.sort_values("wardIndex")
	workplaces = workplaces.sort_values("ID")
	schools = schools.sort_values("ID")
	commonArea = commonArea.sort_values("wardIndex")
	
	individuals['CommunityCentreDistance'] = individuals.apply(getDistances, axis=1, args=(commonArea,))
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

		#Get Distributions
		age_values, age_distribution = compute_age_distribution(ageDistribution)
		household_sizes, household_distribution = compute_household_size_distribution(householdSizes, householdDistribution)
		schoolsize_values, schoolsize_distribution = extrapolate_school_size_distribution(schoolDistribution)
		workplacesize_distribution = workplaces_size_distribution()


		print(max(individuals['CommunityCentreDistance'].values))

		#Age-Distribution fit
		import matplotlib.pyplot as plt

		plt.plot(individuals['age'].value_counts(normalize=True).sort_index(ascending=True), 'r')
		plt.plot(age_distribution, 'b')
		plt.xlabel('Age')
		plt.ylabel('Density')
		plt.title('Distribution of age')
		plt.grid(True)
		plt.xticks(np.arange(0,81,10), np.concatenate((age_values[np.arange(0,71,10)], ['80+'])))
		plt.savefig(path+"/age.png")
		plt.close()



		x = np.unique(individuals['household'].values)
		x = x[~np.isnan(x)]
		households = {'id':x, 'number of people': [0 for i in range(0,len(x))] }
		households = pd.DataFrame(households)
    
		for i in range(0,len(individuals)):
				# print(i/len(individuals))
				
				households.at[households['id']==individuals.loc[i,'household'],'number of people'] = 1+households.loc[households['id']==individuals.loc[i,'household'],'number of people']
    
		#Household-size distribution fit
		HH_ranges = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
		HH_numbers = np.array([len(households.loc[households['number of people']==HH_ranges[i]]) for i in range(0,len(HH_ranges))])
		HH_output_distribution = HH_numbers/sum(HH_numbers)
		plt.plot(HH_ranges,household_distribution)
		plt.plot(HH_ranges,HH_output_distribution,'r')
		plt.xticks(np.arange(1,16,1), np.concatenate((np.array(household_sizes)[np.arange(0,14,1)], ['15+'])) )

		# plt.plot( households['people staying'].value_counts(normalize=True).sort_index(ascending=True), 'r')
		# plt.plot(np.arange(1,len(household_distribution)+1), household_distribution, 'b')
		plt.xlabel('Household size')
		plt.ylabel('Density')
		plt.title('Distribution of household size')
		plt.grid(True)
		plt.savefig(path+"/HH_size.png")
		plt.close()


	else:
		print("instantiation failed, please re-run")
	






instantiate(city=sys.argv[1], targetPopulation=sys.argv[2], averageStudents=sys.argv[3], averageWorkforce=sys.argv[4])