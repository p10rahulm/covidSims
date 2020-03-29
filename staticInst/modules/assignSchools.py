#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright [2020] [Indian Institute of Science, Bangalore]
SPDX-License-Identifier: Apache-2.0
"""
__name__ = "Module to assign individuals to schools"


import os, sys
import json
import pandas as pd
import numpy as np

#Data-processing Functions
from modules.processGeoData import schoolLocation

def assign_schools(individuals, cityGeoDF, schoolDistribution):
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
    student_indices = np.where((individuals['workplaceType']==2).values)[0]
    schools = pd.DataFrame()
    capacities = []
    cumulative_capacity = 0
    while len(student_indices)>cumulative_capacity:
        schools = schools.append(schoolLocation(cityGeoDF,  1),ignore_index=True)
        temp = np.random.choice(schoolsize_values,1,p=schoolsize_distribution)[0]
        capacities.append(temp)
        cumulative_capacity = cumulative_capacity + temp
    schools['ID'] = np.arange(0,len(schools))
    schools['capacity'] = capacities
    schools['strength'] = np.full(len(schools),0)
    schools['students'] = [[] for x in range(0,len(schools))]
    
    
    
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
            # print(i)
            d = schools.loc[i,'capacity'] - schools.loc[i,'strength']
            if len(np.setdiff1d(student_indices, already_assigned_students)) >=d:
                add_to_school_id = np.random.choice(np.setdiff1d(student_indices, already_assigned_students), d, replace=False)
                for j in range(0,d):
                    individuals.at[add_to_school_id[j],'school'] = schools.loc[i,'ID']
                    already_assigned_students.append(add_to_school_id[j])
                    schools.at[i,'students'].append(add_to_school_id[j])
                    schools.at[i,'strength'] = schools.loc[i,'strength']+1
            else:
                add_to_school_id = np.setdiff1d(student_indices, already_assigned_students)
                for j in range(0,len(np.setdiff1d(student_indices, already_assigned_students))):
                    individuals.at[add_to_school_id[j],'school'] = schools.loc[i,'ID']
                    already_assigned_students.append(add_to_school_id[j])
                    schools.at[i,'students'].append(add_to_school_id[j])
                    schools.at[i,'strength'] = schools.loc[i,'strength']+1
 
    return individuals, schools
    