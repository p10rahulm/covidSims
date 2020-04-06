#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright [2020] [Indian Institute of Science, Bangalore]
SPDX-License-Identifier: Apache-2.0
"""
__name__ = "Module to assign individuals to workplaces"

import numpy as np
import pandas as pd 
import math
import scipy.stats as stats
from modules.processGeoData import workplaceLocation


wards = None #global variable to hold the wards DF

def workplaces_size_distribution(a=3.26, c=0.97, m_max=2870):  
    count=1
    a=3.26
    c=0.97
    m_max=2870
    p_nplus = np.arange(float(m_max))
    for m in range(m_max):
        p_nplus[m] =  ((( (1+m_max/a)/(1+m/a))**c) -1) / (((1+m_max/a)**c) -1)

    p_nminus = 1.0 - p_nplus
    p_n = np.arange(float(m_max))
    prev=0.0
    for m in range(1, m_max):
        p_n[m] = p_nminus[m] - prev
        prev = p_nminus[m] 

    return p_n/sum(p_n)

# # findout neighbours of a given ward
# def neighbouring_wards_ids(input_ward):
#     global ward
#     return np.array(str.split(wards.loc[wards['wardNo']==input_ward,'neighbors'].values[0],','),dtype=int)
    
# compute haversine distance
def distance(lat1, lon1, lat2, lon2):
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

def commuter_distance_distribution(m_min,m_max,a,b):
    temp = []
    for d in np.arange(m_min,m_max,0.01):
        temp.append(1/(1+(d/a)**b))
    temp = np.array(temp)
    return temp/np.sum(temp)


def sample_from_commuter_distribution(m_min,m_max,distribution,n):
    return np.random.choice(np.arange(m_min,m_max,0.01),n,p=distribution,replace=True)

# # findout possible wokrplaces for an individual by looking at nearby wards
# def possible_workplaces_ids(input_ward, workplaces):
#     neighbouring_wards = neighbouring_wards_ids(input_ward)
#     temp = []
#     for j in range(0,len(neighbouring_wards)):
#         temp = np.concatenate((temp,np.array(workplaces.loc[workplaces['ward']==neighbouring_wards[j]]['ID'].values) ))
#     return temp

def find_and_assign_workplace(sampled_distances, individuals, workplaces, workers_to_be_assigned_indices, i, already_assigned_workers):
        distances_to_workers = []
        for j in range(0,len(workers_to_be_assigned_indices)):
            distances_to_workers.append(distance(workplaces.loc[i,'lat'],workplaces.loc[i,'lon'],individuals.loc[workers_to_be_assigned_indices[j],'lat'],individuals.loc[workers_to_be_assigned_indices[j],'lon']))
        distances_to_workers = np.array(distances_to_workers)
        temp = []
        temp_indices = []
        for j in range(0,len(sampled_distances)):
            #print(len(distances_to_workers))
            #print(len(workers_to_be_assigned_indices))
            if len(temp_indices)>0:
                distances_to_workers[temp_indices[0]] = np.inf
            temp_index = np.argmin(np.abs(distances_to_workers-sampled_distances[j]))
            individual_index = workers_to_be_assigned_indices[temp_index]
            temp_indices.insert(0,temp_index)
            individuals.at[individual_index,'workplace']  = i
            workplaces.at[i,'workers'].append(individual_index)
            workplaces.at[i,'workforce'] = workplaces.loc[i,'workforce'] + 1 
            workplaces.at[i,'distances'].append(distances_to_workers[temp_index])
            temp.append(individual_index)
            already_assigned_workers.append(individual_index)
        workers_to_be_assigned_indices = np.setdiff1d(workers_to_be_assigned_indices,temp)

def assign_workplaces(cityGeoDF, individuals, maxWorkplaceDistance=35, minWorkplaceDistance=0, maxWorkplaces=2870):
    global m_min, m_max, a, b
    m_min = minWorkplaceDistance
    m_max = maxWorkplaceDistance
    a = 4    #parameter in distribution for commuter distance - Thailand paper
    b = 3.8  #parameter in distribution for commuter distance - Thailand paper

    workers_indices = individuals.index.values#np.where((individuals['workplaceType']==1).values)[0]
    workplaces = pd.DataFrame()
    capacities = []
    cumulative_capacity = 0
    workplacesize_values = np.arange(maxWorkplaces)
    workplacesize_distribution = workplaces_size_distribution()
    while len(workers_indices)>cumulative_capacity:
        workplaces = workplaces.append(workplaceLocation(cityGeoDF,  1),ignore_index=True)
        temp = np.random.choice(workplacesize_values,1,p=workplacesize_distribution)[0]
        capacities.append(temp)
        cumulative_capacity = cumulative_capacity + temp

    workplaces['capacity'] = capacities
    workplaces['workforce'] = np.full(len(workplaces),0)
    workplaces['workers'] = [[] for x in range(0,len(workplaces))]
    workplaces['distances'] = [[] for x in range(0,len(workplaces))]
    workplaces['ID'] = np.arange(0,len(workplaces))
    workplace_distance_distribution = commuter_distance_distribution(m_min,m_max,a,b)
    
    already_assigned_workers = []
    workers_to_be_assigned_indices = workers_indices


    for i in range(0,len(workplaces)):

        if len(workers_to_be_assigned_indices)>=workplaces.loc[i,'capacity']:
            sampled_distances = sample_from_commuter_distribution(m_min,m_max,workplace_distance_distribution,workplaces.loc[i,'capacity'])
            find_and_assign_workplace(sampled_distances, individuals, workplaces, workers_to_be_assigned_indices, i, already_assigned_workers)
           
        else:
            sampled_distances = sample_from_commuter_distribution(m_min,m_max,workplace_distance_distribution,len(workers_to_be_assigned_indices))
            find_and_assign_workplace(sampled_distances, individuals, workplaces, workers_to_be_assigned_indices, i, already_assigned_workers)

    return workplaces, individuals