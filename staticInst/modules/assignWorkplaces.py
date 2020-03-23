#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__name__ = "Module to assign individuals to workplaces or schools"
___author__ = "Sarath"

import numpy as np
import pandas as pd 
from scipy.stats import stats

# generate s sample of size of workplace 
def gen_wp_size(count=1, a=3.26, c=0.97, m_max=2870):
    #function to generate a truncated Zipf sample

    vals = np.arange(m_max)
    p_nplus = np.arange(float(m_max))
    for m in range(m_max):
        p_nplus[m] =  ((( (1+m_max/a)/(1+m/a))**c) -1) / (((1+m_max/a)**c) -1)

    p_nminus = 1.0 - p_nplus
    p_n = np.arange(float(m_max))
    prev=0.0
    for m in range(1, m_max):
        p_n[m] = p_nminus[m] - prev
        prev = p_nminus[m] 

    bzipf = stats.rv_discrete (name='bzipf', values=(vals, p_n))
    rval = bzipf.rvs(size=count)
    #print(rval)
    return rval


# findout neighbours of a given ward
def neighbouring_wards_ids(input_ward):
    return np.array(str.split(wards.loc[wards['Ward No.']==input_ward,'Neighbors'].values[0],','),dtype=int)
    
# compute Euclidean distance    
def distance(lat1, long1, lat2, long2):
    return np.sqrt((lat1 - lat2)**2 + (long1-long2)**2)
    
# findout possible wokrplaces for an individual by looking at nearby wards
def possible_workplaces_ids(input_ward):
    neighbouring_wards = neighbouring_wards_ids(input_ward)
    temp = []
    for j in range(0,len(neighbouring_wards)):
        temp = np.concatenate((temp,np.array(workplaces.loc[workplaces['ward']==neighbouring_wards[j]]['ID'].values) ))
    return temp
    

def assign_schools_and_workplaces(wardNeighbors, workplaces, schools, individuals):
    wards = wardNeighbors
    W = len(wardNeighbors)

    WP = len(workplaces)
    # insert some columns for further processing
    workplaces.insert(2,"workforce", [0 for x in range(0,WP)]) 
    workplaces.insert(3,"workers", [[] for x in range(0,WP)])

    S = len(schools)
    schools.insert(2,"students", [[] for x in range(0,S)])
    workDistance = []

    # generate capacity according to workspace size distribution
    capacity = []
    for i in range(0,WP):
        capacity.append(gen_wp_size()[0])

    workplaces.insert(4,"capacity", capacity)

    # keep track of individuals already assigned
    already_assigned = []
    count = 0
    workforce = []
    # assign individuals
    for i in range(0,len(individuals)):
        # print(i/len(individuals))
        # individuals to workplaces
        if individuals.loc[i,'age']>=22 and individuals.loc[i,'age']<=55: 
            workforce.append(i)
            count = count+1
            lat = individuals.loc[i,'lat']
            long = individuals.loc[i,'lon']
            possible_workplace_ids =  possible_workplaces_ids(individuals.loc[i,'ward'])
            distances = []
            for j in range(0,len(possible_workplace_ids)):
                distances.append(distance(lat,long,workplaces.loc[workplaces['ID']==int(possible_workplace_ids[j]),'location'].values[0][1],workplaces.loc[workplaces['ID']==int(possible_workplace_ids[j]),'location'].values[0][0]))
            distances = np.array(distances)
            distances = distances/sum(distances)
            add_to_workplace_id = int(possible_workplace_ids[np.random.choice(len(possible_workplace_ids),p=distances)])
            if workplaces.loc[workplaces.loc[workplaces['ID']==int(add_to_workplace_id),'ID'].index[0], 'workforce'] < workplaces.loc[workplaces.loc[workplaces['ID']==int(add_to_workplace_id),'ID'].index[0], 'capacity']:
                individuals.at[i,'workplace'] = add_to_workplace_id
                workplaces.at[workplaces.loc[workplaces['ID']==int(add_to_workplace_id),'ID'].index[0],'workforce'] = workplaces.loc[workplaces.loc[workplaces['ID']==int(add_to_workplace_id),'ID'].index[0],'workforce']+1
                workplaces.at[workplaces.loc[workplaces['ID']==int(add_to_workplace_id),'ID'].index[0],'workers'].append(i)
                already_assigned.append(i)
        # individuals to schools - this is done randomly now, Sarath will make sure that marginals are consistent
        elif individuals.loc[i,'age']<=21 and individuals.loc[i,'age']>=5:
            lat = individuals.loc[i,'lat']
            long = individuals.loc[i,'lon']
            possible_school_id = schools.loc[schools['ward']==individuals.loc[i,'ward']]['ID'].values
            index = np.random.choice(len(possible_school_id))
            individuals.at[i,'school'] = possible_school_id[index]
            schools.at[schools.loc[schools['ID']==possible_school_id[index]].index[0],'students'].append(i)

    # randomly assign unassigned individuals to workplaces
    # first check for workplaces that are not full
    for i in range(0,len(workplaces)):
        if workplaces.loc[i,'capacity'] > workplaces.loc[i,'workforce']:
            d = workplaces.loc[i,'capacity'] - workplaces.loc[i,'workforce']
            if len(np.setdiff1d(workforce, already_assigned)) >=d:
                add_to_workplace_id = np.random.choice(np.setdiff1d(workforce, already_assigned), d, replace=False)
                for j in range(0,d):
                    individuals.at[add_to_workplace_id[j],'workplace'] = workplaces.loc[i,'ID']
                    already_assigned.append(add_to_workplace_id[j])
                    workplaces.at[i,'workers'].append(add_to_workplace_id[j])
                    workplaces.at[i,'workforce'] = workplaces.loc[i,'workforce']+1
    for i in range(0,len(individuals)):
        if individuals.loc[i,'age']>=22 and individuals.loc[i,'age']<=55 and (not i in already_assigned):
            lat = individuals.loc[i,'lat']
            long = individuals.loc[i,'lon']
            add_to_workplace_id = np.random.choice(W)
            individuals.at[i,'workplace'] = add_to_workplace_id
            workplaces.at[int(add_to_workplace_id), 'workforce'] =workplaces.loc[int(add_to_workplace_id), 'workforce']+1 
            workplaces.at[int(add_to_workplace_id),'workers'].append(i)
    
    return workplaces, schools, individuals