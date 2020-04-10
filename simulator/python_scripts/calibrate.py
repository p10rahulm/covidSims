#Copyright [2020] [Indian Institute of Science, Bangalore]
#SPDX-License-Identifier: Apache-2.0


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def find_slope(data):
    n = len(data) 
    return np.dot(data, np.arange(1,n+1))/np.sum(np.square(np.arange(1,n+1)))

def calibrate(resolution,number_of_days,count):
    #calibrate the model to match the deceased curve
    
    threshold = 4
    error_tolerence = 1
    slope_tolerence = 0.01
    
    country='India'
    infected = pd.read_csv('./data/ecdp.csv')
    infected.fillna('Nodata')
    infected = i = infected.iloc[::-1]
    
    # read infected and recoverd population
    i = infected.loc[infected['countriesAndTerritories']==country]
    
    dates1 =  np.array(infected.loc[infected['countriesAndTerritories']==country]['dateRep'].values)
    i_data = []
    
    i_data.append(i['cases'].values[0])
    for j in range(1,len(dates1)):
        i_data.append(i_data[j-1] + i['cases'].values[j])
    
    i_data = np.array(i_data)
    
    dead_data = []
    
    dead_data.append(i['deaths'].values[0])
    for j in range(1,len(dates1)):
        dead_data.append(dead_data[j-1] + i['deaths'].values[j])
    
    dead_data = np.array(dead_data)
    
    # can thoreshold i(t):
    
    valid_indices = i_data>=threshold
    i_data = i_data[valid_indices]
    dead_data = dead_data[valid_indices]
    
    # Read output of simulation
    affected_nointervenion = pd.read_csv('./data/affected_mean.csv')
    dead_nointervention = pd.read_csv('./data/dead_mean.csv')
    
    # Extract NumAffected
    dates = affected_nointervenion['timestep'].values
    affected_nointervention =  affected_nointervenion['affected'].values
    dead_nointervention = dead_nointervention['dead'].values
    #affected_nointervention = np.repeat(i_data,4) # regress on the India data
    
    # Start the simulation from the point where it crosses i_data[0]
    start_index = np.min(np.where(affected_nointervention>=i_data[0]))
    # take data from start_index to t0
    t0 = start_index + number_of_days*resolution

    dates = dates[0:t0]
    affected_data_nointervention =  affected_nointervention[start_index:t0]
    dead_data_nointervention = dead_nointervention[start_index:t0]
    dead_data_nointervention = np.take(dead_data_nointervention, np.arange(0,len(dead_data_nointervention),resolution))
    i_data = i_data[0:number_of_days]
    dead_data = dead_data[0:number_of_days]
    
    lambda_h = pd.read_csv('./data/lambda H_mean.csv')['lambda H'][start_index:t0].values[-1]
    lambda_w = pd.read_csv('./data/lambda W_mean.csv')['lambda W'][start_index:t0].values[-1]
    lambda_c = pd.read_csv('./data/lambda C_mean.csv')['lambda C'][start_index:t0].values[-1]
       
    error_vector =  dead_data - dead_data_nointervention
    max_difference = error_vector[np.argmax(np.abs(error_vector))]
    
    lambda_h_diff = (lambda_h-0.33)
    lambda_w_diff = (lambda_w-0.33)
    lambda_c_diff = (lambda_c-0.33)
    
    slope_dead_simulator =  find_slope(dead_data_nointervention[dead_data_nointervention > 0])
    slope_dead_data = find_slope(dead_data[dead_data>0])
    slope_diff = slope_dead_data - slope_dead_simulator
    
    flag = False
    if abs(lambda_h_diff)<0.01 and abs(lambda_w_diff)<0.01 and abs(lambda_c_diff)<0.01 and abs(max_difference) <error_tolerence and abs(slope_diff)<slope_tolerence: 
        flag = True
        return [flag, 0, 0, 0, 0,0]
    else:
        step_beta_h = -1*lambda_h_diff/count
        step_beta_w = -1*lambda_w_diff/count
        step_beta_c = -1*lambda_c_diff/count
        init_frac_scale = min(np.exp(max_difference),1.5)
        beta_mult_factor = min(np.exp(slope_diff),1.5)
        return [flag, init_frac_scale, step_beta_h, step_beta_w, step_beta_c,beta_mult_factor]
