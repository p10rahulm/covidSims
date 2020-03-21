#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 20:49:57 2020

@author: sarathy
"""
import numpy as np
import pandas as pd
import json

N = 1000
dictlist_individuals = [dict() for x in range(N)]

H = int(N/4)
dictlist_houses = [dict() for x in range(H)]

W = 10

# age distribution
age_values = np.arange(0,81,1)
age_distribution_over_gap5 = [9.32, 10.48, 10.96, 9.95, 9.2, 8.38, 7.32, 7.03, 5.98, 5.15, \
                    4.05, 3.23, 3.11, 2.18, 1.59, 0.76, 1.31]

age_distribution = []
for i in range(0,len(age_distribution_over_gap5)-1):
    for j in range(0,5):
        age_distribution.append(age_distribution_over_gap5[i]/5)
age_distribution.append(age_distribution_over_gap5[16])
age_distribution = np.array(age_distribution)
age_distribution = age_distribution/sum(age_distribution)

# household size distributin
household_sizes = [1,2,3,4,5,6]
household_distribution = [0.0459, 0.0717, 0.16155, 0.24575, 0.3234, 0.1517]

# create individuals with desired age distribution
individuals = {'id': np.arange(0,N), 'age':np.random.choice(age_values,N,p=age_distribution), 'household':np.ones((1,N))[0]*-1}
individuals = pd.DataFrame(individuals)

# create households with desired household-size distribution
households = {'id':np.arange(0,H), 'Ward No': np.random.choice(np.arange(0,W),H), 'Lat':np.arange(0,H), 'Long':np.arange(0,H), 'people staying':np.random.choice(household_sizes, H, p=household_distribution), 'individuals':[[] for x in range(0,H)],  'flag':[0 for x in range(0,H)]}
households = pd.DataFrame(households)


# home-people assignment
already_assigned = []

for i in range(0,H):
    #print(i)
    if len(already_assigned)<N-6:
        if households['people staying'].values[i] == 1:
            possible_list = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=22,individuals['age'].values<=30)),already_assigned)]
            if (len(possible_list)>0):
                choose_index = np.random.choice(len(possible_list))
                already_assigned.append(int(possible_list.iloc[choose_index]['id']))
                individuals.at[int(possible_list.iloc[choose_index]['id']),'household']=int(i)
                households.at[i,'individuals'].append(int(possible_list.iloc[choose_index]['id']))
                households.at[i,'flag']=1
        elif households['people staying'].values[i] == 2:
            possible_list = individuals.iloc[np.setdiff1d(np.where(np.logical_and(individuals['age'].values>=22,individuals['age'].values<=30)),already_assigned)]
            if (len(possible_list)>=2):
                choose_index = np.random.choice(len(possible_list),2)
                for j in range(0,len(choose_index)):
                    already_assigned.append(int(possible_list.iloc[choose_index[j]]['id']))
                    individuals.at[int(possible_list.iloc[choose_index[j]]['id']),'household']=int(i)
                    households.at[i,'individuals'].append(int(possible_list.iloc[choose_index[j]]['id']))
                    households.at[i,'flag']=1
        elif households['people staying'].values[i] == 3:
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
                
        elif households['people staying'].values[i] == 4:
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
                    
        elif households['people staying'].values[i] == 5:
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
        else:
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
# assign individuals to 

unassigned_individuals_ids =  individuals.loc[individuals['household']==-1]['id'].values
unassigned_households_ids = households.loc[households['flag']==0]['id'].values
for i in range(0,len(unassigned_households_ids)):
    #print(i)
    #print(len(unassigned_individuals_ids)>=households.loc[i]['people staying'])
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


if len(unassigned_individuals_ids)>0:
    house_indices =  np.random.choice(len(unassigned_households_ids),len(unassigned_individuals_ids), replace=False)
    for j in range(0,len(house_indices)):
        households.at[unassigned_households_ids[house_indices[j]],'people staying'] = households.loc[house_indices[j],'people staying']+1
        households.at[unassigned_households_ids[house_indices[j]],'individuals'].append(unassigned_individuals_ids[j])
        individuals.at[unassigned_individuals_ids[j],'household']=unassigned_households_ids[house_indices[j]]
            
#households = households.drop(columns='flag')