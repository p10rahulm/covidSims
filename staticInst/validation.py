
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

def validate_distributions(city):
    # read parameters based on city
    cityprofile = pd.read_json('./data/base/'+city+'/cityProfile.json')
    m_max_commuter_distance = cityprofile['maxWorkplaceDistance'].values[1]
    ageDistribution = cityprofile['age']['weights']
    householdSizes = cityprofile['householdSize']['bins']
    householdDistribution = cityprofile['householdSize']['weights']
    
    a_workplacesize = 3.26
    c_workplacesize = 0.97
    m_max_workplacesize = 2870
    
    a_commuter_distance = 4
    b_commuter_distance = 3.8 
    m_max_commuter_distance = 130
 
    # create age values and expand the age distirution
    age_values = np.arange(0,81,1)
    age_distribution_over_gap5 = ageDistribution

    age_distribution_over_gap5 = ageDistribution
    age_distribution = []
    for i in range(0,len(age_distribution_over_gap5)-1):
        for j in range(0,5):
            age_distribution.append(age_distribution_over_gap5[i]/5)
    age_distribution.append(age_distribution_over_gap5[16])
    age_distribution = np.array(age_distribution)
    age_distribution = age_distribution/sum(age_distribution)
    
    # create household sizes and spread the distribution if needed
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
    

    # generate workplace size distribution
    a=a_workplacesize
    c=c_workplacesize
    m_max=m_max_workplacesize    
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
        
    # read data frames for validation
    individuals = pd.read_json('./data/'+city+'-100K-300students/individuals.json')
    wp = pd.read_json('./data/'+city+'-100K-300students/workplaces.json')
    
    # create empirical distributions from instantiated city
    # age
    age_output =  [ len(np.where(individuals['age'].values == i)[0]) for i in age_values]/np.sum([ len(np.where(individuals['age'].values == i)[0]) for i in age_values])    
    # household size
    full_frame = np.array([len(np.where(individuals['household'] == i)[0]) for i in np.unique(individuals['household'].values)])    
    householdsize_output = [len(np.where(full_frame == j)[0]) for j in household_sizes]/np.sum([len(np.where(full_frame == j)[0]) for j in household_sizes])    
    # workplace size
    full_frame = np.array([len(np.where(individuals['workplace'] == i)[0]) for i in np.unique(individuals['workplace'].values)[~np.isnan(np.unique(individuals['workplace'].values))]])
    workplacesize_output = [len(np.where(full_frame == j)[0]) for j in workplace_sizes] / np.sum([len(np.where(full_frame == j)[0]) for j in workplace_sizes])    
    # commuter distance
    full_frame = np.array([distance(individuals.loc[i,'lat'],individuals.loc[i,'lon'],wp.loc[wp.index==int(individuals.loc[i,'workplace']),'lat'],wp.loc[wp.index==int(individuals.loc[i,'workplace']),'lon']) for i in np.where(individuals['workplaceType']==1)[0]])        
    commuter_distance_output = [len(np.where(np.array(np.floor(full_frame),dtype=int) ==i)[0]) for i in np.arange(0,m_max_commuter_distance)]/np.sum([len(np.where(np.array(np.floor(full_frame),dtype=int) ==i)[0]) for i in np.arange(0,m_max_commuter_distance)])
    
    # plots
    
    plt.plot(age_output, 'r',label='Instantiation')
    plt.plot(age_distribution,label='Data')
    plt.xlabel('Age')
    plt.ylabel('Density')
    plt.title('Distribution of age')
    plt.grid(True)
    plt.legend()
    plt.xticks(np.arange(0,81,10), np.concatenate((age_values[np.arange(0,71,10)], ['80+'])) )
    plt.savefig('age')
    plt.show()
    
    plt.close()
    
    # plot household size distribution
    #HH_ranges = ['1','2','3','4','5','6','7-10','11-14','15+']
    plt.plot(household_sizes,householdsize_output,'r',label='Instantiation')
    plt.plot(household_sizes,household_distribution,label='Data')
    plt.xticks(household_sizes, np.concatenate((np.array(household_sizes)[np.arange(0,len(household_sizes)-1,1)], [str(household_sizes[-1])])) )
    plt.xlabel('Household size')
    plt.ylabel('Density')
    plt.legend()
    plt.title('Distribution of household size')
    plt.grid(True)
    plt.savefig('household_size')
    plt.show()
    plt.close()
    
    
    workplace_distribution = p_n
    plt.plot(np.log10(workplace_sizes),np.log10(workplacesize_output),'r',label='Instantiation')
    plt.plot(np.log10(workplace_sizes), np.log10(workplace_distribution),label='Model')
    plt.xlabel('Workplace size (log-scale)')
    plt.ylabel('log_10 Density')
    plt.title('Distribution of workplace size (in log-scale)')
    plt.grid(True)
    plt.legend()
    plot_xlabel =  [1, 10, 100, 1000, 2400]
    plot_xlabel1 = np.log10(workplace_sizes)[plot_xlabel]
    plt.xticks(plot_xlabel1, (workplace_sizes)[plot_xlabel])
    plt.savefig('workplace_size')
    plt.show()
    plt.close()
    
    actual_dist=[]
    actual_dist = travel_distance_distribution(0,m_max_commuter_distance,a_commuter_distance,b_commuter_distance)
    d = np.arange(0,m_max_commuter_distance,1)
    plt.plot(np.log10(d),np.log10(actual_dist),'bo-',label='Model')
    plt.plot(np.log10(d),np.log10((commuter_distance_output)),'ro-',label='Instantiation')
    #plt.plot(np.log10(d),np.log10((distances)),'go-',label='Data')
    plt.xlabel('Workplace distance (km) (log-scale)')
    plt.ylabel('log_10 Density')
    plt.title('Distribution of workplace distances')
    plot_xlabel=[1,5,25,31]
    plot_xlabel1 = np.log10(d)[plot_xlabel]
    plt.xticks(plot_xlabel1,d[plot_xlabel])
    plt.grid(True)
    plt.legend()
    plt.savefig('workplace_distance')
    plt.close()
