#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__name__ = "Module to assign individuals to houses"
___author__ = "Sarath"

import numpy as np 
import pandas as pd 

def assign_individuals_to_houses(targetPopulation, wards, totalHousehold, ageDistribution=[0.073, 0.078, 0.083, 0.086, 0.102, 0.11, 0.098, 0.081, 0.071, 0.059, 0.049, 0.037, 0.03, 0.021, 0.01, 0.007, 0.005], householdDistribution=[0.0417, 0.1308, 0.2228, 0.3077, 0.1530, 0.1439]):
    N = targetPopulation
    dictlist_individuals = [dict() for x in range(N)]

    H = totalHousehold
    dictlist_houses = [dict() for x in range(H)]

    W = wards

    # age distribution
    age_values = np.arange(0,81,1)
    age_distribution_over_gap5 = [0.073, 0.078, 0.083, 0.086, 0.102, 0.11, 0.098, 0.081, 0.071, 0.059, 0.049, 0.037, 0.03, 0.021, 0.01, 0.007, 0.005]

    age_distribution = []
    for i in range(0,len(age_distribution_over_gap5)-1):
        for j in range(0,5):
            age_distribution.append(age_distribution_over_gap5[i]/5)
    age_distribution.append(age_distribution_over_gap5[16])
    age_distribution = np.array(age_distribution)
    age_distribution = age_distribution/sum(age_distribution)

    # household size distributin
    household_sizes = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
    household_dist = [0.0417, 0.1308, 0.2228, 0.3077, 0.1530, 0.0726, 0.0645, 0.0054, 0.0015] #1,2,3,4,5,6,7-10,11-14,15+
    household_distribution = household_dist[0:6]
    for i in range(0,4):
        household_distribution.append(household_dist[6]/4)
    for i in range(0,4):
        household_distribution.append(household_dist[7]/4)
    household_distribution.append(household_dist[8])
    household_distribution = np.array(household_distribution)/np.sum(household_distribution)
    mean_household_size = np.matmul(household_sizes, household_distribution)    
    
    # create individuals with desired age distribution
    individuals = {'id': np.arange(0,N), 'age':np.random.choice(age_values,N,p=age_distribution), 'household':np.ones((1,N))[0]*-1}
    individuals = pd.DataFrame(individuals) #after households DF is ready - add lat, lon, ward no to individuals || call functions in workplace_assignment.py

    # create households with desired household-size distribution
    #Ward No, Lat and Lon - would be city data (geojson of city)
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
            elif households['people staying'].values[i] == 6:
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
             
            elif households['people staying'].values[i] == 7:
                
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
    	     
            elif households['people staying'].values[i] == 8:
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
    	               
            elif households['people staying'].values[i] == 9:
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
    	                                   
            elif households['people staying'].values[i] == 10:
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
    	                                   
            elif households['people staying'].values[i] == 11:
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
    	                                   
                        
            elif households['people staying'].values[i] == 12:
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
    	                                   
            elif households['people staying'].values[i] == 13:
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
            elif households['people staying'].values[i] == 14:
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
    
            elif households['people staying'].values[i] == 15:
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
                        
    # assign unassigned individuals to households

    unassigned_individuals_ids =  individuals.loc[individuals['household']==-1]['id'].values
    unassigned_households_ids = households.loc[households['flag']==0]['id'].values
    # first look for any unoccupied household
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
    households = households.loc[households['flag']!=0]
    individuals['household']=individuals['household'].astype(int)
    return individuals, households