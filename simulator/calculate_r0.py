#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 08:08:41 2020

Description: Calculates R0 value from the infected time series as well as 
plots the model against the simulation. Returns R0 for
all intervention strategies as well as no intervention and writes them into 
the csv file r0_values.csv.
Input: t0 - time series will be considered from 0 to t0 for R0 computation.
The script assumes the files my_data_all_together_no_intervention.csv,
my_data_all_together_HQ
my_data_all_together_case_isolation
my_data_all_together_lockdown
in the present directory.

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares


def calculate_r0(t0):

    # read data
    infected_nointervenion = pd.read_csv('./my_data_all_together_no_intervention.csv',header=None)
    infected_hq = pd.read_csv('./my_data_all_together_HQ.csv',header=None)
    infected_ci = pd.read_csv('./my_data_all_together_case_isolation.csv',header=None)
    infected_lockdown = pd.read_csv('./my_data_all_together_lockdown.csv',header=None)
    
    # extract NumInfected for each intervention strategy
    dates = infected_nointervenion[0].values
    i_data_nointervention =  infected_nointervenion[1].values
    i_data_hq =  infected_hq[1].values
    i_data_ci =  infected_ci[1].values
    i_data_lockdown =  infected_lockdown[1].values
    
    # take data from 0 to t0
    dates = dates[0:t0]
    i_data_nointervention =  i_data_nointervention[0:t0]
    i_data_hq =  i_data_hq[0:t0]
    i_data_ci =  i_data_ci[0:t0]
    i_data_lockdown = i_data_lockdown[0:t0]
    
    mu=0.1 # recovery rate
    i0=10 # initial condition
    # objective function for regression
    def objfn_itplusrt_nointervention(param):
        itplusrt = []
        for i in range(0,len(i_data_nointervention)):
            itplusrt.append(i0*((param[0]*np.exp((param[0]-mu)*i)-mu))/(param[0]-mu))  
        return (itplusrt - (i_data_nointervention))
    
    def objfn_itplusrt_hq(param):
        itplusrt = []
        for i in range(0,len(i_data_hq)):
            itplusrt.append(i0*((param[0]*np.exp((param[0]-mu)*i)-mu))/(param[0]-mu))  
        return (itplusrt - (i_data_hq))
    
    def objfn_itplusrt_ci(param):
        itplusrt = []
        for i in range(0,len(i_data_ci)):
            itplusrt.append(i0*((param[0]*np.exp((param[0]-mu)*i)-mu))/(param[0]-mu))  
        return (itplusrt - (i_data_ci))
    
    def objfn_itplusrt_lockdown(param):
        itplusrt = []
        for i in range(0,len(i_data_lockdown)):
            itplusrt.append(i0*((param[0]*np.exp((param[0]-mu)*i)-mu))/(param[0]-mu))  
        return (itplusrt - (i_data_lockdown))
    
    param0=[1]
    
    #regression
    res_nointervention = least_squares(objfn_itplusrt_nointervention, param0, bounds=([0],[np.inf])) 
    res_hq = least_squares(objfn_itplusrt_hq, param0, bounds=([0],[np.inf])) 
    res_ci = least_squares(objfn_itplusrt_ci, param0, bounds=([0],[np.inf])) 
    res_lockdown = least_squares(objfn_itplusrt_lockdown, param0, bounds=([0],[np.inf])) 
    
    predicted_itplusrt = []
    for i in range(0,t0):
        predicted_itplusrt.append(i0*((res_nointervention.x[0]*np.exp((res_nointervention.x[0]-mu)*i)-mu))/(res_nointervention.x[0]-mu))  
    
    plot_xlabels = np.arange(0,len(dates),int(np.floor(len(dates)/4)))
    plt.plot(predicted_itplusrt,'r', label='fit' )
    plt.plot(i_data_nointervention,'bo-', label='simulation')
    plt.xticks(plot_xlabels, dates[plot_xlabels])
    plt.xlabel('Date')
    plt.ylabel('i(t)')
    plt.grid(axis='both')
    plt.legend()
    plt.title('No intervention')
    plt.savefig('nointervention')
    plt.close()
    
    predicted_itplusrt = []
    for i in range(0,t0):
        predicted_itplusrt.append(i0*((res_hq.x[0]*np.exp((res_hq.x[0]-mu)*i)-mu))/(res_hq.x[0]-mu))  
    
    plot_xlabels = np.arange(0,len(dates),int(np.floor(len(dates)/4)))
    plt.plot(predicted_itplusrt,'r', label='fit' )
    plt.plot(i_data_hq,'bo-', label='simulation')
    plt.xticks(plot_xlabels, dates[plot_xlabels])
    plt.xlabel('Date')
    plt.ylabel('i(t)')
    plt.grid(axis='both')
    plt.legend()
    plt.title('Home quarantine')
    plt.savefig('hq')
    plt.close()
    
    predicted_itplusrt = []
    for i in range(0,t0):
        predicted_itplusrt.append(i0*((res_ci.x[0]*np.exp((res_ci.x[0]-mu)*i)-mu))/(res_ci.x[0]-mu))  
    
    plot_xlabels = np.arange(0,len(dates),int(np.floor(len(dates)/4)))
    plt.plot(predicted_itplusrt,'r', label='fit' )
    plt.plot(i_data_ci,'bo-', label='simulation')
    plt.xticks(plot_xlabels, dates[plot_xlabels])
    plt.xlabel('Date')
    plt.ylabel('i(t)')
    plt.grid(axis='both')
    plt.legend()
    plt.title('Case isolation')
    plt.savefig('ci')
    plt.close()
    
    predicted_itplusrt = []
    for i in range(0,t0):
        predicted_itplusrt.append(i0*((res_lockdown.x[0]*np.exp((res_lockdown.x[0]-mu)*i)-mu))/(res_lockdown.x[0]-mu))  
    
    plot_xlabels = np.arange(0,len(dates),int(np.floor(len(dates)/4)))
    plt.plot(predicted_itplusrt,'r', label='fit' )
    plt.plot(i_data_lockdown,'bo-', label='simulation')
    plt.xticks(plot_xlabels, dates[plot_xlabels])
    plt.xlabel('Date')
    plt.ylabel('i(t)')
    plt.grid(axis='both')
    plt.legend()
    plt.title('Lock down')
    plt.savefig('lockdown')
    plt.close()
    
    # all data plots on one graph
    plot_xlabels = np.arange(0,len(dates),int(np.floor(len(dates)/4)))
    plt.plot(i_data_nointervention,'bo-', label='NoIntervention')
    plt.plot(i_data_hq,'ro-', label='HomeQuarantine')
    plt.plot(i_data_ci,'go-', label='CaseIsolation')
    plt.plot(i_data_lockdown,'yo-', label='LockDown')
    plt.xticks(plot_xlabels, dates[plot_xlabels])
    plt.xlabel('Date')
    plt.ylabel('i(t)')
    plt.grid(axis='both')
    plt.legend()
    plt.title('Comparison')
    plt.savefig('allplots')
    plt.close()
    
    column_names = ['NoIntervention', 'HQ', 'CI', 'LockDown']
    pd.DataFrame([[res_nointervention.x[0]/mu, res_hq.x[0]/mu, res_ci.x[0]/mu, res_lockdown.x[0]/mu]], columns = column_names).to_csv('./r0_values.csv', index = False)
    
    return [res_nointervention.x[0]/mu, res_hq.x[0]/mu, res_ci.x[0]/mu, res_lockdown.x[0]/mu]