#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 15:44:45 2020

@author: sarathy
"""

import numpy as np
import scipy.stats as stats

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


def neighbouring_wards_ids(ward):
    return 0
    
def distance(lat1, long1, lat2, long2):
    return np.sqrt((lat1 - lat2)**2 + (long1-long2)**2)
    
def possible_workplaces_ids(ward):
    

    
def workplace_assignment(individuals):
    # set number of workplaces here
    WP = 100
    # generate capacity according to workspace size distribution
    capacity = []
    for i in range(0,WP):
        capacity.append(gen_wp_size()[0])
    
    # keep track of individuals already assigned
    already_assigned = []
    for i in range(0,len(individuals)):
        if individual.loc[i,'age']>=22 and individual.loc[i,'age']<=55: 
            lat = individuals.loc[i,'Lat']
            long = individuals.loc[i,'Long']
            possible_workplaces_ids =  possible_workplaces_ids(individuals.loc[i,'ward'])
            distances = []
            for j in range(0,len(possible_workplaces)):
                distances.append(distance(lat,long,workplaces.iloc[possible_workplaces_ids[j],'Lat'],workplaces.iloc[possible_workplaces_ids[j],'Long']))
            distances = np.array(distances)
            add_to_workplace_id = possible_workplaces_ids[np.random.choice(len(possible_workplaces_ids),p=distances)]
            if workplace.iloc[add_to_workplace_id, 'workforce'] <= capacity(add_to_workplace_id)
                individual.at[i,'workplace'] = add_to_workplace_id
                #workspaces.at[add_to_workplace_id,'flag']=1
            already_assigned.append(i)
    
    
    # randomly assig unassigned individuals
    for i in range(0,len(individuals))
        if individual.loc[i,'age']>=22 and individual.loc[i,'age']<=55 and (not i in already_assigned):
            lat = individuals.loc[i,'Lat']
            long = individuals.loc[i,'Long']
            add_to_workplace_id = np.random.choice(W)
            individual.at[i,'workplace'] = add_to_workplace_id
    
    
            