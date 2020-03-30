#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""
Copyright [2020] [Indian Institute of Science, Bangalore]
SPDX-License-Identifier: Apache-2.0
""""
__name__ = "validation script for data vs model validation"

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
import math

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

def travel_distance_distribution(m_min,m_max,a,b):
    temp = []
    for d in np.arange(m_min,m_max,1):
        temp.append(1/(1+(d/a)**b))
    temp = np.array(temp)
    return temp/np.sum(temp)

def validate_distributions(ageDistribution,householdDistribution,schoolsizeDistribution):
# age distribution
    age_values = np.arange(0,81,1)
    age_distribution_over_gap5 = ageDistribution

    age_distribution = []
    for i in range(0,len(age_distribution_over_gap5)-1):
        for j in range(0,5):
            age_distribution.append(age_distribution_over_gap5[i]/5)
    age_distribution.append(age_distribution_over_gap5[16])
    age_distribution = np.array(age_distribution)
    age_distribution = age_distribution/sum(age_distribution)
    
    household_sizes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    household_dist = householdDistribution  #1,2,3,4,5,6,7-10,11-14,15+
    household_distribution = household_dist[0:6]
    for i in range(0,4):
        household_distribution.append(household_dist[6]/4)
    for i in range(0,4):
        household_distribution.append(household_dist[7]/4)
    household_distribution.append(household_dist[8])
    household_distribution = np.array(household_distribution)/np.sum(household_distribution)
    # generate s sample of size of workplace 
    a=3.26
    c=0.97
    m_max=2870
        #function to generate a truncated Zipf sample
    
    workplace_sizes = np.arange(m_max)
    p_nplus = np.arange(float(m_max))
    for m in range(m_max):
        p_nplus[m] =  ((( (1+m_max/a)/(1+m/a))**c) -1) / (((1+m_max/a)**c) -1)
    
    p_nminus = 1.0 - p_nplus
    p_n = np.arange(float(m_max))
    prev=0.0
    for m in range(1, m_max):
        p_n[m] = p_nminus[m] - prev
        prev = p_nminus[m] 
    
    bzipf = stats.rv_discrete (name='bzipf', values=(workplace_sizes, p_n))
    

    individuals = pd.read_json('./data/bangalore/individuals.json')
    
    age = {'id':np.unique(individuals['age'].values), 'number of people':[0 for i in range(0,len(np.unique(individuals['age'].values)))]}
    age = pd.DataFrame(age)
    x = np.unique(individuals['household'].values)
    x = x[~np.isnan(x)]
    households = {'id':x, 'number of people': [0 for i in range(0,len(x))] }
    households = pd.DataFrame(households)
    
    x = np.unique(individuals['school'].values)
    x = x[~np.isnan(x)]
    schools = {'id':x, 'number of people': [0 for i in range(0,len(x))] }
    schools = pd.DataFrame(schools)
    
    x = np.unique(individuals['workplace'].values)
    x = x[~np.isnan(x)]
    
    workplaces = {'id':x, 'number of people': [0 for i in range(0,len(x))]}
    workplaces = pd.DataFrame(workplaces)
    workplace_distances = []    
    wp = pd.read_json('./data/bangalore/workplaces.json')
    
    for i in range(0,len(individuals)):
        print(i/len(individuals))
        age.at[age['id']==individuals.loc[i,'age'],'number of people'] = 1+age.loc[age['id']==individuals.loc[i,'age'],'number of people']
        
        households.at[households['id']==individuals.loc[i,'household'],'number of people'] = 1+households.loc[households['id']==individuals.loc[i,'household'],'number of people']
    
        if not(np.isnan(individuals.loc[i,'school'])):
            schools.at[schools['ID']==individuals.loc[i,'school'],'number of people'] = 1+schools.loc[schools['ID']==individuals.loc[i,'school'],'strength']
            
        if not(np.isnan(individuals.loc[i,'workplace'])):
            workplaces.at[workplaces.index==int(individuals.loc[i,'workplace']),'workforce'] = 1+workplaces.loc[workplaces.index==individuals.loc[i,'workplace'],'workforce']
            workplace_distances.append(distance(individuals.loc[i,'lat'],individuals.loc[i,'lon'],wp.loc[wp.index==int(individuals.loc[i,'workplace']),'lat'],wp.loc[wp.index==int(individuals.loc[i,'workplace']),'lon']))
    # plot age distribution
    plt.plot(age['number of people'].values/(np.sum(age['number of people'].values)), 'r')
    plt.plot(age_distribution)
    plt.xlabel('Age')
    plt.ylabel('Density')
    plt.title('Distribution of age')
    plt.grid(True)
    plt.xticks(np.arange(0,81,10), np.concatenate((age_values[np.arange(0,71,10)], ['80+'])) )
    plt.savefig('age')
    plt.show()
    
    plt.close()
    
    # plot household size distribution
    #HH_ranges = ['1','2','3','4','5','6','7-10','11-14','15+']
    HH_ranges = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    HH_numbers = np.array([len(households.loc[households['number of people']==HH_ranges[i]]) for i in range(0,len(HH_ranges))])
    HH_output_distribution = HH_numbers/sum(HH_numbers)
    plt.plot(HH_ranges,household_distribution)
    plt.plot(HH_ranges,HH_output_distribution,'r')
    plt.xticks(np.arange(1,16,1), np.concatenate((np.array(household_sizes)[np.arange(0,14,1)], ['15+'])) )
    plt.xlabel('Household size')
    plt.ylabel('Density')
    plt.title('Distribution of household size')
    plt.grid(True)
    plt.savefig('household_size')
    plt.show()
    plt.close()
    
    WP_ranges = workplace_sizes
    WP_numbers = np.array([len(workplaces.loc[workplaces['workforce']==WP_ranges[i]]) for i in range(0,len(WP_ranges))])
    #WP_capacity = np.array([len(workplaces.loc[workplaces['capacity']==WP_ranges[i]]) for i in range(0,len(WP_ranges))])
    #WP_capacity = WP_capacity/sum(WP_capacity)
    WP_output_distribution = WP_numbers/sum(WP_numbers)
    workplace_distribution = p_n
    plt.plot(np.log(workplace_sizes), np.log(workplace_distribution))
    plt.plot(np.log(workplace_sizes),np.log(WP_output_distribution),'r')
    plt.xlabel('Workplace size (log-scale)')
    plt.ylabel('log-Density')
    plt.title('Distribution of workplace size (in log-scale)')
    plt.grid(True)
    plot_xlabel =  [1, 10, 100, 1000, 2400]
    #plot_ylabel = [1, 5, 25,  125, 625, 1000, 2400]
    plot_xlabel1 = np.log(workplace_sizes)[plot_xlabel]
    #plot_ylabel1 = np.log(workplace_distribution[plot_ylabel])
    #plt.yticks(plot_ylabel1, workplace_distribution[plot_xlabel])
    plt.xticks(plot_xlabel1, (workplace_sizes)[plot_xlabel])
    plt.savefig('workplace_size')
    plt.show()
    plt.close()
    
    workplace_distance_empirical =  np.zeros((1,len(np.arange(m_min,m_max,1))))[0]
    for j in range(0,len(workplace_distances)):
        workplace_distance_empirical[int(workplace_distances[j])]+=1
    workplace_distance_empirical = workplace_distance_empirical/np.sum(workplace_distance_empirical)
    actual_dist=[]
    actual_dist = travel_distance_distribution(m_min,m_max,4,3.8)
    d = np.arange(0,35,1)
    plt.plot(np.log10(d),np.log10(actual_dist))
    plt.plot(np.log10(d),np.log10((workplace_distance_empirical)),'r')
    plt.xlabel('Workplace distance (km) (log-scale)')
    plt.ylabel('log-Density')
    plt.title('Distribution of workplace distances')
    plot_xlabel=[1,5,25,34]
    plot_xlabel1 = np.log10(d)[plot_xlabel]
    plt.xticks(plot_xlabel1,d[plot_xlabel])
    plt.grid(True)
    plt.savefig('workplace_distance')
    plt.show()
    plt.close()
    
    # create workplace distances