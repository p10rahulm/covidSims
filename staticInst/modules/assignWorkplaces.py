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

# findout possible wokrplaces for an individual by looking at nearby wards
def possible_workplaces_ids(input_ward, workplaces):
    neighbouring_wards = neighbouring_wards_ids(input_ward)
    temp = []
    for j in range(0,len(neighbouring_wards)):
        temp = np.concatenate((temp,np.array(workplaces.loc[workplaces['ward']==neighbouring_wards[j]]['ID'].values) ))
    return temp
    

def assign_schools_and_workplaces(demographics, workplaces, schools, individuals, schoolsNeeded, schoolDistribution=[0.0184, 0.1204, 0.2315, 0.2315, 0.1574, 0.0889, 0.0630, 0.0481, 0.0278, 0.0130]):
    global wards
    # generate workplaces size distribution
    count=1
    a=3.26
    c=0.97
    m_max=2870
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

    #scale number of workplaces by population
   
    bzipf = stats.rv_discrete (name='bzipf', values=(vals, p_n))
    
    # generate schools size distribution
    schoolsize_values = np.arange(50,901,1)
    schoolsize_distribution_over_gap100 = schoolDistribution # 50-99, 100-199, ..., 800 - 899, 900+
    schoolsize_distribution = []
    for i in range(1,len(schoolsize_distribution_over_gap100)-1):
        for j in range(0,100):
            schoolsize_distribution.append(schoolsize_distribution_over_gap100[i]/100)

    for i in range(0,50):
        schoolsize_distribution.insert(0,schoolsize_distribution_over_gap100[0]/50)

    schoolsize_distribution.append(schoolsize_distribution_over_gap100[len(schoolsize_distribution_over_gap100)-1])
    schoolsize_distribution = np.array(schoolsize_distribution)
    schoolsize_distribution = schoolsize_distribution/np.sum(schoolsize_distribution)
    mean_schoolsize = np.matmul(schoolsize_values, schoolsize_distribution)

    #scale number of school sizes by population
    school_scaling_factor = schoolsNeeded / mean_schoolsize
    schoolsize_values = [int(value*school_scaling_factor) for value in schoolsize_values]

    wards = demographics[['wardNo', 'wardIndex', 'neighbors']]
    W = len(wards)
    WP = len(workplaces)
    # insert some columns for further processing
    workplaces.insert(2,"workforce", [0 for x in range(0,WP)]) 
    workplaces.insert(3,"workers", [[] for x in range(0,WP)])

    S = len(schools)
    schools.insert(2,"students", [[] for x in range(0,S)])
    schools.insert(3,"strength", [0 for x in range(0,S)])
    schools.insert(4,"capacity", np.random.choice(schoolsize_values, S, p=schoolsize_distribution))

    workDistance = []

    # generate capacity according to workspace size distribution
    capacity = []
    for i in range(0,WP):
        capacity.append(bzipf.rvs(size=1)[0])

    workplaces.insert(4,"capacity", capacity)

    # keep track of individuals already assigned
    already_assigned = []
    count = 0
    workforce = []
    studentforce = []
    already_assigned_students = []
    # assign individuals
    for i in range(0,len(individuals)):
        # print(i/len(individuals))
        # individuals to workplaces
        if individuals.loc[i,'age']>=22 and individuals.loc[i,'age']<=55: 
            workforce.append(i)
            count = count+1
            lat = individuals.loc[i,'lat']
            long = individuals.loc[i,'lon']
            possible_workplace_ids =  possible_workplaces_ids(individuals.loc[i,'wardNo'], workplaces)
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
        # individuals to schools 
        elif individuals.loc[i,'age']<=21 and individuals.loc[i,'age']>=5:
            studentforce.append(i)
            lat = individuals.loc[i,'lat']
            long = individuals.loc[i,'lon']
            possible_school_id1 = schools.loc[schools['ward']==individuals.loc[i,'wardNo']]['ID'].values
            possible_school_id = []
            if len(possible_school_id1) > 0:
                for j in range(0,len(possible_school_id1)):
                    if schools.loc[schools.loc[schools['ID']==possible_school_id1[j],'ID'].index[0],'capacity'] > schools.loc[schools.loc[schools['ID']==possible_school_id1[j],'ID'].index[0],'strength']:
                        possible_school_id.append(possible_school_id1[j])
                possible_school_id = np.array(possible_school_id)
            if len(possible_school_id) > 0:
                index = np.random.choice(len(possible_school_id))
                individuals.at[i,'school'] = possible_school_id[index]
                schools.at[schools.loc[schools['ID']==possible_school_id[index]].index[0],'students'].append(i)
                schools.at[schools.loc[schools['ID']==possible_school_id[index]].index[0],'strength'] = schools.loc[schools.loc[schools['ID']==possible_school_id[index]].index[0],'strength'] +1 
                already_assigned_students.append(i)

                
    # randomly assign unassigned individuals to workplaces and schools
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

    # first check if schools are not full
    for i in range(0,len(schools)):
        if schools.loc[i,'capacity'] > schools.loc[i,'strength']:
            d = schools.loc[i,'capacity'] - schools.loc[i,'strength']
            if len(np.setdiff1d(studentforce, already_assigned_students)) >=d:
                add_to_school_id = np.random.choice(np.setdiff1d(studentforce, already_assigned_students), d, replace=False)
                for j in range(0,d):
                    individuals.at[add_to_school_id[j],'school'] = schools.loc[i,'ID']
                    already_assigned_students.append(add_to_school_id[j])
                    schools.at[i,'students'].append(add_to_school_id[j])
                    schools.at[i,'strength'] = schools.loc[i,'strength']+1

    # if anyone has unassigned workplace or school, assign him/her randomly
    for i in range(0,len(individuals)):
        if individuals.loc[i,'age']>=22 and individuals.loc[i,'age']<=55 and (not i in already_assigned):
            lat = individuals.loc[i,'lat']
            long = individuals.loc[i,'lon']
            add_to_workplace_id = np.random.choice(WP)
            individuals.at[i,'workplace'] = add_to_workplace_id
            workplaces.at[int(add_to_workplace_id), 'workforce'] =workplaces.loc[int(add_to_workplace_id), 'workforce']+1 
            workplaces.at[int(add_to_workplace_id),'workers'].append(i)

        elif individuals.loc[i,'age']<=21 and individuals.loc[i,'age']>=5 and (not i in already_assigned_students):
            lat = individuals.loc[i,'lat']
            long = individuals.loc[i,'lon']
            add_to_school_id = np.random.choice(S)
            individuals.at[i,'school'] = add_to_school_id
            schools.at[int(add_to_school_id), 'strength'] =schools.loc[int(add_to_school_id), 'strength']+1 
            schools.at[int(add_to_school_id),'students'].append(i)
    # workplaces = workplaces.sort_values("ID")
    # schools = schools.sort_values("ID")
    # individuals = individuals.sort_values("id")
    return workplaces, schools, individuals