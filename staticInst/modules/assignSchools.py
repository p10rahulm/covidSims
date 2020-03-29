#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 04:21:48 2020

@author: sarathy
"""

import os, sys
import json
import pandas as pd
import numpy as np

#Data-processing Functions
from modules.processDemographics import *
from modules.processGeoData import *

def assign_schools(individuals,cityGeoDF,schoolsize_values, schoolsize_distribution):
    student_indices = np.where((individuals['work/school']==2).values)[0]
    schools = pd.DataFrame({})
    capacities = []
    cumulative_capacity = 0
    while len(student_indices)>cumulative_capacity:
        schools = schools.append(schoolLocation(cityGeoDF,  1),ignore_index=True)
        temp = np.random.choice(schoolsize_values,1,p=schoolsize_distribution)[0]
        capacities.append(temp)
        cumulative_capacity = cumulative_capacity + temp
    schools.insert(3,'capacity',capacities)
    schools.insert(4,'strength',np.full(len(schools),0))
    schools.insert(5,'students',[[] for x in range(0,len(schools))])
    schools['ID'] = np.arange(0,len(schools))
    
    
    already_assigned_students = []
    for i in student_indices:
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

    # check if schools are not full
    for i in range(0,len(schools)):
        if schools.loc[i,'capacity'] > schools.loc[i,'strength']:
            print(i)
            d = schools.loc[i,'capacity'] - schools.loc[i,'strength']
            if len(np.setdiff1d(student_indices, already_assigned_students)) >=d:
                add_to_school_id = np.random.choice(np.setdiff1d(student_indices, already_assigned_students), d, replace=False)
                for j in range(0,d):
                    individuals.at[add_to_school_id[j],'school'] = schools.loc[i,'ID']
                    already_assigned_students.append(add_to_school_id[j])
                    schools.at[i,'students'].append(add_to_school_id[j])
                    schools.at[i,'strength'] = schools.loc[i,'strength']+1
            else:
                print(1)
                add_to_school_id = np.setdiff1d(student_indices, already_assigned_students)
                for j in range(0,len(np.setdiff1d(student_indices, already_assigned_students))):
                    individuals.at[add_to_school_id[j],'school'] = schools.loc[i,'ID']
                    already_assigned_students.append(add_to_school_id[j])
                    schools.at[i,'students'].append(add_to_school_id[j])
                    schools.at[i,'strength'] = schools.loc[i,'strength']+1
 
    
    return individuals, schools
    