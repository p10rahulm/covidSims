#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 08:08:41 2020

Description: Calculates R0 value from the infected time series as well as 
plots the model against the simulation. Returns R0 for no intervention strategy.

Inputs:
threshold: Start when the actual data is more than this threshold.
number of days - number of days for calibration starting from threshold.
resolution: number of steps in a day. resolution=1 means that 1 data point per day.
The script assumes the simulator output files infected_mean.csv and
recovered_mean.csv, and the India data file ecdp.csv in the present directory.

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares


def calculate_r0(threshold,number_of_days,resolution):
    # Process India data
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
    # can thoreshold i(t):
    
    valid_indices = i_data>=threshold
    i_data = i_data[valid_indices]
    
    # Read output of simulation
    infected_nointervenion = pd.read_csv('./data/infected_mean.csv')
    recovered_nointervention = pd.read_csv('./data/recovered_mean.csv')
    
    # Extract NumInfected+NumRecovered
    dates = infected_nointervenion['timestep'].values
    i_data_nointervention =  infected_nointervenion['infected'].values
    r_data_nointervention = recovered_nointervention['recovered'].values
    iplusr_nointervention = i_data_nointervention + r_data_nointervention
    #iplusr_nointervention = np.repeat(i_data,4) # regress on the India data
    
    # Start the simulation from the point where it crosses i_data[0]
    start_index = np.min(np.where(iplusr_nointervention>=i_data[0]))
    # take data from start_index to t0
    t0 = start_index + number_of_days*resolution

    dates = dates[0:t0]
    iplusr_data_nointervention =  iplusr_nointervention[start_index:t0]
     
    mu=0.1/resolution # recovery rate

    # objective function for regression
    def objfn_itplusrt_nointervention(param):
        itplusrt = []
        for i in range(0,len(iplusr_data_nointervention)):
            itplusrt.append(param[1]*((param[0]*np.exp((param[0]-mu)*i)-mu))/(param[0]-mu))  
        itplusrt = np.array(itplusrt)
        return (np.log10(itplusrt) - np.log10(iplusr_data_nointervention))
    
    
    param0=[4*mu,10]
    
    #regression
    res_nointervention = least_squares(objfn_itplusrt_nointervention, param0, bounds=([0,0],[np.inf,np.inf])) 
    
    predicted_itplusrt = []
    for i in range(0,len(iplusr_data_nointervention)):
        predicted_itplusrt.append(res_nointervention.x[1]*((res_nointervention.x[0]*np.exp((res_nointervention.x[0]-mu)*i)-mu))/(res_nointervention.x[0]-mu))  

    plot_xlabels = [0,10,20,26] #np.arange(0,int(len(iplusr_data_nointervention)/5),5)
    plt.plot(np.log10(np.take(predicted_itplusrt,np.arange(0,len(predicted_itplusrt),4))),'r', label='fit' )
    plt.plot(np.log10(np.take(iplusr_data_nointervention,np.arange(0,len(iplusr_data_nointervention),4))),'bo-', label='simulation')
    plt.plot(np.log10(i_data),'go-', label='India Data')
    plt.xticks(plot_xlabels,["Mar 5", "Mar 15", "Mar 25", "Mar 31"])
    plt.xlabel('Date')
    plt.ylabel('log_10 NumInfected+NumRecovered')

    plt.grid(axis='both')
    plt.legend()
    plt.title('No intervention')
    plt.savefig('./data/nointervention_logscale')
    plt.close()

    plot_xlabels = [0,10,20,26] #np.arange(0,int(len(iplusr_data_nointervention)/5),5)
    plt.plot((np.take(predicted_itplusrt,np.arange(0,len(predicted_itplusrt),4))),'r', label='fit' )
    plt.plot((np.take(iplusr_data_nointervention,np.arange(0,len(iplusr_data_nointervention),4))),'bo-', label='simulation')
    plt.plot((i_data),'go-', label='India Data')
    plt.xticks(plot_xlabels,["Mar 5", "Mar 15", "Mar 25", "Mar 31"])
    plt.xlabel('Date')
    plt.ylabel('NumInfected+NumRecovered')

    plt.grid(axis='both')
    plt.legend()
    plt.title('No intervention')
    plt.savefig('./data/nointervention')
    plt.close()
    
    return res_nointervention.x[0]/mu
