#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright [2020] [Indian Institute of Science, Bangalore]
SPDX-License-Identifier: Apache-2.0
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, MultiPolygon


def seedIndividuals(city):
    cityDF = gpd.read_file("./data/base/"+city+"/city.geojson")
    
    individuals = pd.read_json('./data/'+city+'-100K-300students/individuals.json')
    N = len(individuals)
    seed_file = pd.read_csv('./data/base/'+city+'/seed_file.csv')
    
    seed = pd.DataFrame({ "infection_status": np.full(N,0), "time_of_infection": np.full(N,0), "time_of_hospitalisation":np.full(N,0)})
    
    wards = []
    for i in range(0,len(seed_file)):
        cases_lt = float(seed_file.loc[i,'LatLong'].split(', ')[0])
        cases_ln = float(seed_file.loc[i,'LatLong'].split(', ')[1])
        point = Point(cases_ln, cases_lt)
        for j in range(0,len(cityDF)):
            if MultiPolygon(cityDF.loc[j,'geometry']).contains(point):
                wards.append(cityDF.loc[j,'wardNo'])
                break
    wards=np.array(wards)
    seed_file.insert(seed_file.shape[1],"ward", wards)
    # first, find dates and arrange from 1 onwards
    temp  = []
    for i in range(0,len(seed_file)):
        date = seed_file.loc[i,'date_onset_symptoms'].split('.')
        if date[2]=='2019' and date[1]=='12':
            temp.append(int(date[0]))
        elif date[2]=='2020' and date[1]=='01':
            temp.append(int(date[0])+31)
    first_symptoms_day_offset = min(temp)
    
        
    for i in range(0,len(seed_file)):
        age = min(seed_file.loc[i,'age'],80)
        ward = seed_file.loc[i,'ward']
        # first check if there is an individual with excat age and ward
        possible_individual_ids = np.where(np.logical_and(individuals['age'].values==age,individuals['wardNo'].values==ward))[0]
        possible_individual_ids = np.setdiff1d(possible_individual_ids, possible_individual_ids[np.where(seed.loc[possible_individual_ids,'infection_status'].values==1)[0]])
        if len(possible_individual_ids) > 0:
            date = seed_file.loc[i,'date_onset_symptoms'].split('.')
            if date[2]=='2019' and date[1]=='12':
                day = int(date[0])-first_symptoms_day_offset
            elif date[2]=='2020' and date[1]=='01':
                day = int(date[0])+31 - first_symptoms_day_offset
            hospital_admission = seed_file.loc[i,'date_admission_hospital'].split('.')
            if hospital_admission[2]=='2019' and hospital_admission[1]=='12':
               hospitalised_day = int(hospital_admission[0]) - first_symptoms_day_offset
            elif hospital_admission[2]=='2020' and hospital_admission[1]=='01':
               hospitalised_day = int(hospital_admission[0]) + 31 - first_symptoms_day_offset
            seed.at[possible_individual_ids[0],'infection_status'] = 1
            seed.at[possible_individual_ids[0],'time_of_infection'] = day
            seed.at[possible_individual_ids[0],'time_of_hospitalisation'] = hospitalised_day
        else: # if not, increase the age band to age-3, age+2 and search. if not found, ignore the seed.
            possible_individual_ids = np.where(np.logical_and(np.isin(individuals['age'].values,np.arange(age-3,age+2)),individuals['wardNo'].values==ward))[0]
            possible_individual_ids = np.setdiff1d(possible_individual_ids, possible_individual_ids[np.where(seed.loc[possible_individual_ids,'infection_status'].values==1)[0]])
            if len(possible_individual_ids) > 0:
                date = seed_file.loc[i,'date_onset_symptoms'].split('.')
                if date[2]=='2019' and date[1]=='12':
                    day = int(date[0])-first_symptoms_day_offset
                elif date[2]=='2020' and date[1]=='01':
                    day = int(date[0])+31 - first_symptoms_day_offset
                hospital_admission = seed_file.loc[i,'date_admission_hospital'].split('.')
                if hospital_admission[2]=='2019' and hospital_admission[1]=='12':
                   hospitalised_day = int(hospital_admission[0]) - first_symptoms_day_offset
                elif hospital_admission[2]=='2020' and hospital_admission[1]=='01':
                   hospitalised_day = int(hospital_admission[0]) + 31 - first_symptoms_day_offset
                seed.at[possible_individual_ids[0],'infection_status'] = 1
                seed.at[possible_individual_ids[0],'time_of_infection'] = day
                seed.at[possible_individual_ids[0],'time_of_hospitalisation'] = hospitalised_day
    # write files
    individuals = individuals.set_index("id")
    individuals['infection_status'] = seed['infection_status'].values
    individuals['time_of_infection'] = seed['time_of_infection'].values
    individuals['time_of_hospitalisation'] = seed['time_of_hospitalisation'].values
    individuals = individuals.reset_index()
    individuals.to_json('./data/'+city+'-100K-300students/individuals.json',orient='records')
    
    
    return seed