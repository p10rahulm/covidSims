#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright [2020] [Indian Institute of Science, Bangalore]
SPDX-License-Identifier: Apache-2.0
"""
__name__ = "Module to assign individuals to workplaces or schools"

import numpy as np
import pandas as pd 
import math
import scipy.stats as stats


wards = None #global variable to hold the wards DF

# findout neighbours of a given ward
def neighbouring_wards_ids(input_ward):
    global ward
    return np.array(str.split(wards.loc[wards['wardNo']==input_ward,'neighbors'].values[0],','),dtype=int)
    
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

# findout possible wokrplaces for an individual by looking at nearby wards
def possible_workplaces_ids(input_ward, workplaces):
    neighbouring_wards = neighbouring_wards_ids(input_ward)
    temp = []
    for j in range(0,len(neighbouring_wards)):
        temp = np.concatenate((temp,np.array(workplaces.loc[workplaces['ward']==neighbouring_wards[j]]['ID'].values) ))
    return temp
    

def assign_workplaces(demographics,individuals):
    workers_indices = np.where((individuals['work/school']==1).values)[0]
    workplaces = pd.DataFrame({})
    capacities = []
    cumulative_capacity = 0
    while len(workers_indices)>cumulative_capacity:
        workplaces = workplaces.append(workplaceLocation(cityGeoDF,  1),ignore_index=True)
        temp = np.random.choice(workplacesize_values,1,p=workplacesize_distribution)[0]
        capacities.append(temp)
        cumulative_capacity = cumulative_capacity + temp
    workplaces.insert(3,'capacity',capacities)
    workplaces.insert(4,'workforce',np.full(len(workplaces),0))
    workplaces.insert(5,'workers',[[] for x in range(0,len(workplaces))])
    workplaces.insert(6,'distances', [[] for x in range(0,len(workplaces))])
    workplaces['ID'] = np.arange(0,len(workplaces))
    workplace_distance_distribution = commuter_distance_distribution(m_min,m_max,a,b)
    
    already_assigned_workers = []
    workers_to_be_assigned_indices = workers_indices
    for i in range(0,len(workplaces)):
        lat = individuals.loc[i,'lat']
        long = individuals.loc[i,'lon']
        if len(workers_to_be_assigned_indices)>=workplaces.loc[i,'capacity']:
            sampled_distances = sample_from_commuter_distribution(m_min,m_max,workplace_distance_distribution,workplaces.loc[i,'capacity'])
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
        else:
            sampled_distances = sample_from_commuter_distribution(m_min,m_max,workplace_distance_distribution,len(workers_to_be_assigned_indices))
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
    return workplaces, individuals