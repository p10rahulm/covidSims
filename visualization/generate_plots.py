#Copyright [2020] [Indian Institute of Science, Bangalore]
#SPDX-License-Identifier: Apache-2.0

import numpy as np
import os
import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt

sim_data_dir = '/home/nihesh/Documents/COVID-19/sim_data/'
file_folder_list = os.listdir(sim_data_dir)

no_data_dir = ['Results', 'combined_plots', 'combined_plots_200K']

for file_folder_name in file_folder_list:
    if (os.path.isdir(sim_data_dir+file_folder_name) and no_data_dir.count(file_folder_name)==0):

        data_dir = sim_data_dir+file_folder_name+'/'
        result_dir = '/home/nihesh/Documents/COVID-19/sim_data_means/'+file_folder_name+'/'
        file_list = os.listdir(data_dir)

        if not (os.path.exists(result_dir)):
            os.mkdir(result_dir)    
        
        print (data_dir)
        column_names = ['timestep', 'affected', 'recovered', 'infected', 'exposed', 'hospitalised', 'critical', 'dead']
        master_df = pd.DataFrame(columns=column_names)

        for file_name in file_list:
            if (file_name.endswith('.csv')):
                file_type = 1 if (len(file_name.split('_'))==3) else 0
                if (file_type):
                    print ('My data file...')
                    '''
                    df = pd.read_csv(data_dir+file_name, header=None)
                    df.columns = ['timestep', 'ward_no', 'infected', 'affected', 'hospitalised', 'critical', 'dead']
                    print (df)
                    '''
                else:
                    print ('My data all together file:', file_name)
                    df = pd.read_csv(data_dir+file_name, header=None)
                    df.columns = ['timestep', 'affected', 'recovered', 'infected', 'exposed', 'hospitalised', 'critical', 'dead']
                    master_df = master_df.append(df)

        master_df[['timestep', 'affected', 'recovered', 'infected', 'exposed', 'hospitalised', 'critical', 'dead']] = master_df[['timestep', 'affected', 'recovered', 'infected', 'exposed', 'hospitalised', 'critical', 'dead']].apply(pd.to_numeric)

        plot_values = ['affected', 'hospitalised', 'infected', 'critical', 'dead']
        plot_title = ['Affected (cum.)', 'Hospitalised (daily)', 'Infected (daily)', 'Critical (daily)', 'Fatalities (cum.)']

        for i in range(len(plot_values)):
            val = plot_values[i]
            plt.figure(figsize=(13,5))
            sns.set()
            df = master_df[['timestep', val]]
            df_mean = df.groupby(['timestep']).mean()
            '''
            df_std = df.groupby(['timestep']).std()
            lower_bound = df_mean - df_std
            upper_bound = df_mean + df_std
            lower_bound[lower_bound < 0] = 0
            df_mean['timestep'] = np.arange(0, 200, 0.25)
            df_std['timestep'] = np.arange(0, 200, 0.25)
            ax = sns.lineplot(x='timestep', y=val, data=df_mean)
            ax.fill_between(df_mean['timestep'], lower_bound[val], upper_bound[val], alpha=0.4)
            ax.set_title('Covid-19 Simulation \nNum '+plot_title[i]+' per 200,000', weight='bold')
            ax.set_xlabel('Days')
            ax.set_ylabel('Num '+plot_title[i]+' per 200,000')
            ax.legend(labels=['Lockdown, Case Isolation and Home Quarantine'], loc=2, fontsize='12')
            ax.figure.savefig(result_dir+val+'_sd.png')
            '''
            df_mean.to_csv(result_dir+val+'_mean.csv')
