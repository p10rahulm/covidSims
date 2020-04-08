#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright [2020] [Indian Institute of Science, Bangalore]
SPDX-License-Identifier: Apache-2.0
"""
__name__ = "Module to assign individuals to houses"

import numpy as np 
import pandas as pd 

def compute_age_distribution(ageDistribution):
    age_values = np.arange(0,81,1)
    age_distribution_over_gap5 = ageDistribution

    age_distribution = []
    for i in range(0,len(age_distribution_over_gap5)-1):
        for j in range(0,5):
            age_distribution.append(age_distribution_over_gap5[i]/5)
    age_distribution.append(age_distribution_over_gap5[16])
    age_distribution = np.array(age_distribution)
    age_distribution = age_distribution/sum(age_distribution)
    return age_values, age_distribution

def initialize_individuals(ageDistribution, targetPopulation):
    age_values, age_distribution = compute_age_distribution(ageDistribution)

    individuals = pd.DataFrame()
    individuals['id'] = np.arange(0,targetPopulation)
    individuals['age'] = np.random.choice(age_values,targetPopulation,p=age_distribution)
    individuals['household'] = -1
    individuals['workplaceType'] = 0
    return individuals

def split_individuals_by_age(individuals, unemployment_fraction):
    # index 2-school, 1-work
    working_15_19 = np.setdiff1d((np.multiply(np.random.choice([0,1],len(np.where(np.logical_and(individuals['age']>=15, individuals['age']<=19).values)[0]),replace=True),np.where(np.logical_and(individuals['age']>=15, individuals['age']<=19).values)[0])),[0])
    schooling_15_19 = np.setdiff1d( np.where(np.logical_and(individuals['age']>=15, individuals['age']<=19).values)[0] , working_15_19)
    # children_indices = np.where(np.logical_and(individuals['age']>=5, individuals['age']<=14).values)[0]
    workers_indices  = np.unique(np.multiply(np.random.choice([0,1],len(np.where(np.logical_and(individuals['age']>=20, individuals['age']<=59).values)[0]),p=[unemployment_fraction,1-unemployment_fraction],replace=True),np.where(np.logical_and(individuals['age']>=20, individuals['age']<=59).values)[0]))
   
    individuals.at[schooling_15_19,'workplaceType'] = 2
    individuals.at[working_15_19,'workplaceType'] = 1
    individuals.loc[(individuals['age']>=5) & (individuals['age']<=14),'workplaceType'] = 2 
    # individuals.at[children_indices,'workplaceType'] = 2
    individuals.at[workers_indices,'workplaceType'] = 1

    return individuals


def compute_household_size_distribution(householdSizes, householdDistribution):
    household_sizes = [] 
    household_dist = []
    for i in range(len(householdSizes)):
        size = householdSizes[i]
        if "-" in size:
            size = size.split('-')
            diff = int(size[1]) - int(size[0]) + 1 #inclusive difference where you want the first number to be present
            for j in range(diff):
                household_sizes.append(int(size[0])+j)
                household_dist.append(householdDistribution[i]/diff)
        elif "+" in size: #last index
            size = int(size.split("+")[0])
            household_sizes.append(size)
            household_dist.append(householdDistribution[i])
        else:
            household_sizes.append(int(householdSizes[i]))
            household_dist.append(householdDistribution[i])

    household_distribution = np.array(household_dist)/np.sum(household_dist)
    return household_sizes, household_distribution


def initialize_households(targetPopulation, wards, householdSizes, householdDistribution):
    households = pd.DataFrame()

    household_sizes, household_distribution = compute_household_size_distribution(householdSizes, householdDistribution)
    mean_household_size = np.matmul(household_sizes, household_distribution)    
    print("mean household size",  mean_household_size)
    H = int(targetPopulation/mean_household_size)
    
    households['id'] = np.arange(0,H)
    households['wardIndex'] = np.random.choice(np.arange(0,wards),H)
    households['people staying'] = np.random.choice(household_sizes, H, p=household_distribution)
    households['individuals'] = [[] for value in range(H)]
    households['flag'] = 0
    households = households.sort_values('people staying')
    return households

# home-people assignment
already_assigned = [] # This is a globally shared variable

def assign_individuals_to_houses(targetPopulation, wards, ageDistribution, householdSizes, householdDistribution,unemployment_fraction):

    individuals = initialize_individuals(ageDistribution, targetPopulation)
    households = initialize_households(targetPopulation, wards, householdSizes, householdDistribution)

    #assign workplace type by age
    individuals = split_individuals_by_age(individuals, unemployment_fraction)

    for i in range(len(households)):
        houseSize = households.loc[i, 'people staying']

        if houseSize == 1:
            households, individuals = hh_1_person(households, individuals, targetPopulation, i)


        if houseSize == 2:
            households, individuals = hh_2_person(households, individuals, targetPopulation, i)


        if houseSize == 3:
            households, individuals = hh_3_person(households, individuals, targetPopulation, i)


        if houseSize == 4:
            households, individuals = hh_4_person(households, individuals, targetPopulation, i)


        if houseSize == 5:
            households, individuals = hh_5_person(households, individuals, targetPopulation, i)
            

        if houseSize == 6:
            households, individuals = hh_6_person(households, individuals, targetPopulation, i)


        if houseSize == 7:
            households, individuals = hh_7_person(households, individuals, targetPopulation, i)


        if houseSize == 8:
            households, individuals = hh_8_person(households, individuals, targetPopulation, i)
            

        if houseSize == 9:
            households, individuals = hh_9_person(households, individuals, targetPopulation, i)
            
        if houseSize == 10:
            households, individuals = hh_10_person(households, individuals, targetPopulation, i)
            
        if houseSize == 11:
            households, individuals = hh_11_person(households, individuals, targetPopulation, i)
            
        if houseSize == 12:
            households, individuals = hh_12_person(households, individuals, targetPopulation, i)

        if houseSize == 13:
            households, individuals = hh_13_person(households, individuals, targetPopulation, i)
    
        if houseSize == 14:
            households, individuals = hh_14_person(households, individuals, targetPopulation, i)
            
        if houseSize == 15:
            households, individuals = hh_15_person(households, individuals, targetPopulation, i)
            
    #assign previously unassigned individuals  
    individuals, households = assign_unassigned_individuals(households, individuals)
    return households, individuals

def hh_1_person(households, individuals, N, i):
        global already_assigned
    # #for i in households.index.values:
        if len(already_assigned)<N-6:
            possible_list = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=22,individuals['age'].values<=30)),already_assigned)]
            if (len(possible_list)>0):
                choose_index = np.random.choice(len(possible_list))
                already_assigned.append(int(possible_list.iloc[choose_index]['id']))
                individuals.at[int(possible_list.iloc[choose_index]['id']),'household']=int(i)
                households.at[i,'individuals'].append(int(possible_list.iloc[choose_index]['id']))
                households.at[i,'flag']=1
        return households, individuals
 
def hh_2_person(households, individuals, N, i):
        global already_assigned
    #for i in households.index.values:
        if len(already_assigned)<N-6:
            possible_list = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=22,individuals['age'].values<=30)),already_assigned)]
            if (len(possible_list)>=2):
                choose_index = np.random.choice(len(possible_list),2)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1
        return households, individuals


def hh_3_person(households, individuals, N, i):
        global already_assigned
    #for i in households.index.values:
        if len(already_assigned)<N-6:
            possible_list1 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=22,individuals['age'].values<=40)),already_assigned)]
            if np.random.choice(1)==1:
                possible_list2 = individuals.iloc[np.setdiff1d(np.where(individuals['age'].values<=10),already_assigned)]
            else:
                possible_list2 = individuals.iloc[np.setdiff1d(np.where(individuals['age'].values>=60),already_assigned)]

            if (len(possible_list1)>=2) and (len(possible_list2)>=1):
                choose_index = np.random.choice(len(possible_list1),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list1.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list1.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list1.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list2))
                already_assigned.append(int(possible_list2.iloc[choose_index]['id']))
                individuals.at[int(possible_list2.iloc[choose_index]['id']),'household']=int(i)
                households.at[i,'individuals'].append(int(possible_list2.iloc[choose_index]['id']))                    
                households.at[i,'flag']=1
        return households, individuals

def hh_4_person(households, individuals, N, i):
        global already_assigned
    #for i in households.index.values:
        if len(already_assigned)<N-6:
            possible_list1 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=30,individuals['age'].values<=55)),already_assigned)]
            possible_list2 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=5,individuals['age'].values<=30)),already_assigned)]

            if (len(possible_list1)>=2) and (len(possible_list2)>=2):
                choose_index = np.random.choice(len(possible_list1),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list1.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list1.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list1.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list2),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list2.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list2.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list2.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1
        return households, individuals


def hh_5_person(households, individuals, N, i):
        global already_assigned
    #for i in households.index.values:
        if len(already_assigned)<N-6:
            possible_list1 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=40,individuals['age'].values<=55)),already_assigned)]
            possible_list2 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=5,individuals['age'].values<=21)),already_assigned)]
            possible_list3 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=22,individuals['age'].values<=30)),already_assigned)]
            if (len(possible_list1)>=2) and (len(possible_list2)>=2) and (len(possible_list3)>=1):
                choose_index = np.random.choice(len(possible_list1),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list1.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list1.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list1.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list2),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list2.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list2.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list2.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list3))
                already_assigned.append(int(possible_list3.iloc[choose_index]['id']))
                individuals.at[int(possible_list3.iloc[choose_index]['id']),'household']=int(i)
                households.at[i,'individuals'].append(int(possible_list3.iloc[choose_index]['id']))
                households.at[i,'flag']=1
        return households, individuals


def hh_6_person(households, individuals, N, i):
        global already_assigned
    #for i in households.index.values:
        if len(already_assigned)<N-6:
            possible_list1 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=21,individuals['age'].values<=30)),already_assigned)]
            possible_list2 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=45,individuals['age'].values<=55)),already_assigned)]
            possible_list3 = individuals.iloc[np.setdiff1d(np.where(individuals['age'].values>=65),already_assigned)]
            if (len(possible_list1)>=2) and (len(possible_list2)>=2) and (len(possible_list3)>=2):
                choose_index = np.random.choice(len(possible_list1),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list1.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list1.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list1.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list2),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list2.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list2.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list2.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list3),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list3.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list3.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list3.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1
        return households, individuals

def hh_7_person(households, individuals, N, i):
        global already_assigned
    #for i in households.index.values:
        if len(already_assigned)<N-6:
            possible_list1 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=21,individuals['age'].values<=30)),already_assigned)]
            possible_list2 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=45,individuals['age'].values<=55)),already_assigned)]
            possible_list3 = individuals.iloc[np.setdiff1d(np.where(individuals['age'].values>=65),already_assigned)]
            possible_list4 = individuals.iloc[np.setdiff1d(np.where(individuals['age'].values<=20),already_assigned)]
            if (len(possible_list1)>=2) and (len(possible_list2)>=2) and (len(possible_list3)>=2) and (len(possible_list4)>=1):
                choose_index = np.random.choice(len(possible_list1),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list1.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list1.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list1.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list2),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list2.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list2.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list2.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list3),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list3.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list3.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list3.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1
                    
                choose_index = np.random.choice(len(possible_list4),1, replace=False)
                already_assigned.append(int(possible_list4.iloc[choose_index]['id']))
                individuals.at[int(possible_list4.iloc[choose_index]['id']),'household']=int(i)
                households.at[i,'individuals'].append(int(possible_list4.iloc[choose_index]['id']))
                households.at[i,'flag']=1
        return households, individuals


def hh_8_person(households, individuals, N, i):
        global already_assigned
    #for i in households.index.values:
        if len(already_assigned)<N-6:
            possible_list1 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=21,individuals['age'].values<=30)),already_assigned)]
            possible_list2 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=45,individuals['age'].values<=55)),already_assigned)]
            possible_list3 = individuals.iloc[np.setdiff1d(np.where(individuals['age'].values>=65),already_assigned)]
            possible_list4 = individuals.iloc[np.setdiff1d(np.where(individuals['age'].values<=20),already_assigned)]
            if (len(possible_list1)>=2) and (len(possible_list2)>=2) and (len(possible_list3)>=2) and (len(possible_list4)>=2):
                choose_index = np.random.choice(len(possible_list1),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list1.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list1.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list1.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list2),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list2.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list2.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list2.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list3),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list3.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list3.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list3.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1
                    
                choose_index = np.random.choice(len(possible_list4),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list4.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list4.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list4.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1
        return households, individuals


def hh_9_person(households, individuals, N, i):
        global already_assigned
    #for i in households.index.values:
        if len(already_assigned)<N-6:
            possible_list1 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=21,individuals['age'].values<=30)),already_assigned)]
            possible_list2 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=45,individuals['age'].values<=55)),already_assigned)]
            possible_list3 = individuals.iloc[np.setdiff1d(np.where(individuals['age'].values>=65),already_assigned)]
            possible_list4 = individuals.iloc[np.setdiff1d(np.where(individuals['age'].values<=20),already_assigned)]
            if (len(possible_list1)>=2) and (len(possible_list2)>=2) and (len(possible_list3)>=2) and (len(possible_list4)>=3):
                choose_index = np.random.choice(len(possible_list1),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list1.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list1.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list1.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list2),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list2.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list2.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list2.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list3),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list3.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list3.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list3.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1
                    
                choose_index = np.random.choice(len(possible_list4),3, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list4.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list4.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list4.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1
        return households, individuals

def hh_10_person(households, individuals, N, i):
        global already_assigned
    #for i in households.index.values:
        if len(already_assigned)<N-6:
            possible_list1 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=21,individuals['age'].values<=30)),already_assigned)]
            possible_list2 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=45,individuals['age'].values<=55)),already_assigned)]
            possible_list3 = individuals.iloc[np.setdiff1d(np.where(individuals['age'].values>=65),already_assigned)]
            possible_list4 = individuals.iloc[np.setdiff1d(np.where(individuals['age'].values<=20),already_assigned)]
            if (len(possible_list1)>=2) and (len(possible_list2)>=2) and (len(possible_list3)>=2) and (len(possible_list4)>=4):
                choose_index = np.random.choice(len(possible_list1),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list1.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list1.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list1.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list2),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list2.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list2.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list2.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list3),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list3.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list3.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list3.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1
                    
                choose_index = np.random.choice(len(possible_list4),4, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list4.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list4.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list4.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1
        return households, individuals


def hh_11_person(households, individuals, N, i):
        global already_assigned
    #for i in households.index.values:
        if len(already_assigned)<N-6:
            possible_list1 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=21,individuals['age'].values<=30)),already_assigned)]
            possible_list2 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=45,individuals['age'].values<=55)),already_assigned)]
            possible_list3 = individuals.iloc[np.setdiff1d(np.where(individuals['age'].values>=65),already_assigned)]
            possible_list4 = individuals.iloc[np.setdiff1d(np.where(individuals['age'].values<=20),already_assigned)]
            if (len(possible_list1)>=3) and (len(possible_list2)>=2) and (len(possible_list3)>=2) and (len(possible_list4)>=4):
                choose_index = np.random.choice(len(possible_list1),3, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list1.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list1.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list1.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list2),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list2.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list2.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list2.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list3),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list3.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list3.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list3.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1
                    
                choose_index = np.random.choice(len(possible_list4),4, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list4.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list4.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list4.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1
        return households, individuals


def hh_12_person(households, individuals, N, i):
        global already_assigned
    #for i in households.index.values:
        if len(already_assigned)<N-6:
            possible_list1 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=21,individuals['age'].values<=30)),already_assigned)]
            possible_list2 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=45,individuals['age'].values<=55)),already_assigned)]
            possible_list3 = individuals.iloc[np.setdiff1d(np.where(individuals['age'].values>=65),already_assigned)]
            possible_list4 = individuals.iloc[np.setdiff1d(np.where(individuals['age'].values<=20),already_assigned)]
            if (len(possible_list1)>=4) and (len(possible_list2)>=2) and (len(possible_list3)>=2) and (len(possible_list4)>=4):
                choose_index = np.random.choice(len(possible_list1),4, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list1.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list1.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list1.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list2),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list2.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list2.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list2.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list3),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list3.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list3.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list3.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1
                    
                choose_index = np.random.choice(len(possible_list4),4, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list4.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list4.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list4.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1
        return households, individuals


def hh_13_person(households, individuals, N, i):
        global already_assigned
    #for i in households.index.values:
        if len(already_assigned)<N-6:
            possible_list1 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=21,individuals['age'].values<=30)),already_assigned)]
            possible_list2 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=45,individuals['age'].values<=55)),already_assigned)]
            possible_list3 = individuals.iloc[np.setdiff1d(np.where(individuals['age'].values>=65),already_assigned)]
            possible_list4 = individuals.iloc[np.setdiff1d(np.where(individuals['age'].values<=20),already_assigned)]
            if (len(possible_list1)>=4) and (len(possible_list2)>=2) and (len(possible_list3)>=3) and (len(possible_list4)>=4):
                choose_index = np.random.choice(len(possible_list1),4, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list1.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list1.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list1.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list2),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list2.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list2.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list2.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list3),3, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list3.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list3.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list3.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1
                    
                choose_index = np.random.choice(len(possible_list4),4, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list4.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list4.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list4.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1
        return households, individuals


def hh_14_person(households, individuals, N, i):
        global already_assigned
    #for i in households.index.values:
        if len(already_assigned)<N-6:
            possible_list1 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=21,individuals['age'].values<=30)),already_assigned)]
            possible_list2 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=45,individuals['age'].values<=55)),already_assigned)]
            possible_list3 = individuals.iloc[np.setdiff1d(np.where(individuals['age'].values>=65),already_assigned)]
            possible_list4 = individuals.iloc[np.setdiff1d(np.where(individuals['age'].values<=20),already_assigned)]
            if (len(possible_list1)>=5) and (len(possible_list2)>=2) and (len(possible_list3)>=3) and (len(possible_list4)>=4):
                choose_index = np.random.choice(len(possible_list1),5, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list1.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list1.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list1.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list2),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list2.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list2.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list2.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list3),3, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list3.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list3.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list3.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1
                    
                choose_index = np.random.choice(len(possible_list4),4, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list4.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list4.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list4.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1
    
        return households, individuals


def hh_15_person(households, individuals, N, i):
        global already_assigned
    #for i in households.index.values:
        if len(already_assigned)<N-6:
            possible_list1 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=21,individuals['age'].values<=30)),already_assigned)]
            possible_list2 = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=45,individuals['age'].values<=55)),already_assigned)]
            possible_list3 = individuals.iloc[np.setdiff1d(np.where(individuals['age'].values>=65),already_assigned)]
            possible_list4 = individuals.iloc[np.setdiff1d(np.where(individuals['age'].values<=20),already_assigned)]
            if (len(possible_list1)>=6) and (len(possible_list2)>=2) and (len(possible_list3)>=3) and (len(possible_list4)>=4):
                choose_index = np.random.choice(len(possible_list1),6, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list1.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list1.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list1.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list2),2, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list2.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list2.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list2.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1

                choose_index = np.random.choice(len(possible_list3),3, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list3.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list3.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list3.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1
                    
                choose_index = np.random.choice(len(possible_list4),4, replace=False)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list4.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list4.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list4.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1     

        return households, individuals



def assign_unassigned_individuals(households, individuals):
    unassigned_individuals_ids =  individuals.loc[individuals['household']==-1]['id'].values
    unassigned_households_ids = households.loc[households['flag']==0]['id'].values
    # first look for any unoccupied household
    for i in range(0,len(unassigned_households_ids)):
        if len(unassigned_individuals_ids)>=households.loc[unassigned_households_ids[i],'people staying']:
            indices = np.random.choice(len(unassigned_individuals_ids), households.loc[unassigned_households_ids[i]]['people staying'], replace=False)
            ind_ids = unassigned_individuals_ids[indices]
            households.at[unassigned_households_ids[i],'flag']=1
            for j in range(0,len(ind_ids)):
                households.at[unassigned_households_ids[i],'individuals'].append(ind_ids[j])
                individuals.at[ind_ids[j],'household'] = int(unassigned_households_ids[i])             
            #print(len(unassigned_individuals_ids))
            unassigned_individuals_ids = np.setdiff1d(unassigned_individuals_ids,ind_ids)

    unassigned_households_ids = households.loc[households['flag']==0]['id'].values

    # if any more unassigned individuals, randomly assign them to houses and increase the household size
    if len(unassigned_individuals_ids)>0:
        if len(unassigned_households_ids)>0:
            for j in range(0,len(unassigned_individuals_ids)):
                house_index = np.random.choice(len(unassigned_households_ids))
                individuals.at[unassigned_individuals_ids[j],'household'] = unassigned_households_ids[house_index]
                #households.at[unassigned_households_ids[house_index],'people staying'] = households.loc[house_index,'people staying'] + 1
                households.at[unassigned_households_ids[house_index],'flag'] = 1
                households.at[unassigned_households_ids[house_index], 'individuals'].append(unassigned_individuals_ids[j])
        else:
            house_indices =  np.random.choice(len(households),len(unassigned_individuals_ids), replace=False)
            for j in range(0,len(unassigned_individuals_ids)):
                households.at[house_indices[j],'people staying'] = households.loc[house_indices[j],'people staying']+1
                households.at[house_indices[j],'individuals'].append(unassigned_individuals_ids[j])
                individuals.at[unassigned_individuals_ids[j],'household']=house_indices[j]
                households.at[house_indices[j],'flag'] = 1
                households.at[house_indices[j], 'individuals'].append(unassigned_individuals_ids[j])

    unassigned_households_ids = households.loc[households['flag']==0]['id'].values
    return individuals, households