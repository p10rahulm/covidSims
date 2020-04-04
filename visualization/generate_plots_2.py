#Copyright [2020] [Indian Institute of Science, Bangalore]
#SPDX-License-Identifier: Apache-2.0

import numpy as np
import os
import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt

def get_stats(df):
    df_means = df.groupby(['timestep']).mean()
    df_std = df.groupby(['timestep']).std()
    lower_band = df_means - df_std
    upper_band = df_means + df_std
    lower_band[lower_band < 0] = 0
    return ([df_means, df_std, lower_band, upper_band])

def combine_data_stats(ni_df, hq_df, ci_df, val):
    df_means_1, df_std_1, lower_band_1, upper_band_1 = get_stats(ni_df)
    df_means_2, df_std_2, lower_band_2, upper_band_2 = get_stats(hq_df)
    df_means_3, df_std_3, lower_band_3, upper_band_3 = get_stats(ci_df)
    master_df = pd.DataFrame({'timestep': np.arange(0, 200, 0.25),
                              'scenario': 'no_intervention',
                              'mean': df_means_1[val], 
                              'std': df_std_1[val],
                              'lower': lower_band_1[val],
                              'upper': upper_band_1[val]})
    master_df = master_df.append(pd.DataFrame({'timestep': np.arange(0, 200, 0.25),
                              'scenario': 'home_quarantine',
                              'mean': df_means_2[val], 
                              'std': df_std_2[val],
                              'lower': lower_band_2[val],
                              'upper': upper_band_2[val]}))
    master_df = master_df.append(pd.DataFrame({'timestep': np.arange(0, 200, 0.25),
                              'scenario': 'case_isolation',
                              'mean': df_means_3[val], 
                              'std': df_std_3[val],
                              'lower': lower_band_3[val],
                              'upper': upper_band_3[val]}))
    return (master_df)

no_intervention_data_dir = '/home/nihesh/Documents/COVID-19/sim_data/no_intervention_200K/'
home_quarantine_data_dir = '/home/nihesh/Documents/COVID-19/sim_data/home_quarantine_200K/'
case_isolation_data_dir = '/home/nihesh/Documents/COVID-19/sim_data/case_isolation_200K/'
result_dir = '/home/nihesh/Documents/COVID-19/sim_data/combined_plots_200K/'
file_list = os.listdir(no_intervention_data_dir)

column_names = ['timestep', 'affected', 'recovered', 'infected', 'exposed', 'hospitalised', 'critical', 'dead']
no_intervention_df = pd.DataFrame(columns=column_names)
home_quarantine_df = pd.DataFrame(columns=column_names)
case_isolation_df = pd.DataFrame(columns=column_names)

for file_name in file_list:
    if (file_name.endswith('.csv')):
        file_type = 1 if (len(file_name.split('_'))==3) else 0
        if (file_type):
            '''
            print ('My data file...')
            df = pd.read_csv(data_dir+file_name, header=None)
            df.columns = ['timestep', 'ward_no', 'infected', 'affected', 'hospitalised', 'critical', 'dead']
            print (df)
            '''
        else:
            df_1 = pd.read_csv(no_intervention_data_dir+file_name, header=None)
            df_1.columns = ['timestep', 'affected', 'recovered', 'infected', 'exposed', 'hospitalised', 'critical', 'dead']
            df_2 = pd.read_csv(home_quarantine_data_dir+file_name, header=None)
            df_2.columns = ['timestep', 'affected', 'recovered', 'infected', 'exposed', 'hospitalised', 'critical', 'dead']
            df_3 = pd.read_csv(case_isolation_data_dir+file_name, header=None)
            df_3.columns = ['timestep', 'affected', 'recovered', 'infected', 'exposed', 'hospitalised', 'critical', 'dead']
            no_intervention_df = no_intervention_df.append(df_1)
            home_quarantine_df = home_quarantine_df.append(df_2)
            case_isolation_df = case_isolation_df.append(df_3)

no_intervention_df[['timestep', 'affected', 'recovered', 'infected', 'exposed', 'hospitalised', 'critical', 'dead']] = no_intervention_df [['timestep', 'affected', 'recovered', 'infected', 'exposed', 'hospitalised', 'critical', 'dead']].apply(pd.to_numeric)
home_quarantine_df[['timestep', 'affected', 'recovered', 'infected', 'exposed', 'hospitalised', 'critical', 'dead']] = home_quarantine_df[['timestep', 'affected', 'recovered', 'infected', 'exposed', 'hospitalised', 'critical', 'dead']].apply(pd.to_numeric)
case_isolation_df[['timestep', 'affected', 'recovered', 'infected', 'exposed', 'hospitalised', 'critical', 'dead']] = case_isolation_df [['timestep', 'affected', 'recovered', 'infected', 'exposed', 'hospitalised', 'critical', 'dead']].apply(pd.to_numeric)

plot_values = ['affected', 'hospitalised', 'infected', 'critical', 'dead']
plot_title = ['Affected (cum.)', 'Hospitalised (daily)', 'Infected (daily)', 'Critical (daily)', 'Fatalities (cum.)']

no_intervention_df['scenario'] = 'no_intervention'
home_quarantine_df['scenario'] = 'home_quarantine'
case_isolation_df['scenario'] = 'case_isolation'

for i in range(len(plot_values)):
    val = plot_values[i]
    plt.figure(figsize=(13,5))
    sns.set()
    #master_df = combine_data_stats(no_intervention_df[['timestep', val]], home_quarantine_df[['timestep', val]], case_isolation_df[['timestep', val]], val)  
    master_df = no_intervention_df.append(home_quarantine_df.append(case_isolation_df))
    ax = sns.lineplot(x='timestep', y=val, data=master_df, ci='sd', hue='scenario')
    #ax = sns.lineplot(x='timestep', y='mean', data=master_df, hue='scenario')
    ax.set_title('Covid-19 Simulation \nNum '+plot_title[i]+' per 200,000', weight='bold')
    ax.set_xlabel('Days')
    ax.set_ylabel('Num '+plot_title[i]+' per 200,000')
    ax.legend(labels=['No Intervention', 'Home Quarantine', 'Case Isolation'], loc=2, fontsize='12')
    ax.figure.savefig(result_dir+val+'_sd.png')
