#Copyright [2020] [Indian Institute of Science, Bangalore]
#SPDX-License-Identifier: Apache-2.0


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import least_squares

def find_slope(data):
    n = len(data) 
    return np.dot(data, np.arange(1,n+1))/np.sum(np.square(np.arange(1,n+1)))

def find_slope_from_regression(data):
    param0 = [1,data[0]]
    n = len(data)
    def obj_fn(param):
        return (param[1]+param[0]*np.arange(0,n)) - data    
    return least_squares(obj_fn,param0).x[0]

def calibrate(resolution,count):
    #calibrate the model to match the deceased curve
    
    threshold = 10 # lower threshold on dead_data
    error_tolerence = 1 # tolerence on shift
    slope_tolerence = 0.01 # tolerence on slope
    lower_threshold = 10  # lower threshold for simulated dead_mean
    upper_threshold = 50  # upper threshold for simulated dead_mean
    
    # set the target lambdas
    lambda_h_target = 0.333333
    lambda_w_target = 0.333333
    lambda_c_target = 0.333334

    # read data from ecdp file
    country='India'
    infected = pd.read_csv('./data/ecdp.csv')
    infected.fillna('Nodata')
    infected = infected.iloc[::-1]
    
    # read dead population
    i = infected.loc[infected['countriesAndTerritories']==country]
    
    dates1 =  np.array(infected.loc[infected['countriesAndTerritories']==country]['dateRep'].values)
    
    # make cumulative death count
    dead_data = []
    dead_data.append(i['deaths'].values[0])
    for j in range(1,len(dates1)):
        dead_data.append(dead_data[j-1] + i['deaths'].values[j])
    
    dead_data = np.array(dead_data)
       
    # read simulation data and consider data based on threshold
    dead_simulation = pd.read_csv('./data/dead_mean.csv')['dead'].values
    
    # keep track of the shift in data
    shift_in_data = np.min(np.where(dead_data>=threshold)[0]) - 61 # to make it start from March 1st
    
    # plot dead_data and dead_simulation. assumes that dead_data starts on March 2st and 
    plt.plot(dead_data[61:len(dead_data)],label='India Data')
    plt.plot(np.take(dead_simulation,np.arange(0,len(dead_simulation),resolution)),'ro-', label='Simulation')
    plt.xlabel('Date')
    plt.grid(True)
    plt.xlabel('Days (starting March 1st)')
    plt.ylabel('Deceased Population')
    plt.savefig('./data/combined_plot_linear_scale')
    plt.close()

    plt.plot(np.log10(dead_data[61:len(dead_data)]),label='India Data')
    plt.plot(np.log10(np.take(dead_simulation,np.arange(0,len(dead_simulation),resolution))),'ro-', label='Simulation')
    plt.xlabel('Date')
    plt.grid(True)
    plt.xlabel('Days (starting March 1st)')
    plt.ylabel('log_10 Deceased Population')
    plt.savefig('./data/combined_plot_log_scale')
    plt.close()      
    # consider data of interest based on threshold
    dead_data = dead_data[dead_data>=threshold] #Add [0:10] for NY and wuhan!
     
    indices_of_interest = np.where(np.logical_and(dead_simulation>=lower_threshold, dead_simulation<=upper_threshold))
    dead_simulation = dead_simulation[indices_of_interest]
     
    # downsample simulation data
    dead_simulation = np.take(dead_simulation, np.arange(0,len(dead_simulation),resolution))
    
    # read lambda values from the simulation    
    lambda_h = pd.read_csv('./data/lambda H_mean.csv')['lambda H'].values[-1]
    lambda_w = pd.read_csv('./data/lambda W_mean.csv')['lambda W'].values[-1]
    lambda_c = pd.read_csv('./data/lambda C_mean.csv')['lambda C'].values[-1]
    
    lambda_h_diff = (lambda_h-lambda_h_target)
    lambda_w_diff = (lambda_w-lambda_w_target)
    lambda_c_diff = (lambda_c-lambda_c_target)
    
    slope_dead_simulator =  find_slope_from_regression(np.log(dead_simulation))
    slope_dead_data = find_slope_from_regression(np.log(dead_data))
    slope_diff = slope_dead_data - slope_dead_simulator
    
    flag = False
    
    # if slopes match, report delay
    if abs(lambda_h_diff)<0.01 and abs(lambda_w_diff)<0.01 and abs(lambda_c_diff)<0.01 and abs(slope_diff)<slope_tolerence: 
        flag = True
        return [flag, 1, 0,0, 0, shift_in_data - indices_of_interest[0][0]/resolution]
    # if not, calibrate for slope
    else:
        step_beta_h = -1*lambda_h_diff/(10+count)
        step_beta_w = -1*lambda_w_diff/(10+count)
        step_beta_c = -1*lambda_c_diff/(10+count)
        beta_scale_factor = max(min(np.exp(slope_diff),1.5), 0.66)
        return [flag, beta_scale_factor, step_beta_h, step_beta_w, step_beta_c,0]
    
