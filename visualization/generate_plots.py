#Copyright [2020] [Indian Institute of Science, Bangalore]
#SPDX-License-Identifier: Apache-2.0

import os
import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt

data_dir = '/Users/nihesh/Desktop/Sim_data/old_sim_data_2/'
result_dir = './Results/'
file_list = os.listdir(data_dir)

column_names = ['timestep', 'affected', 'recovered', 'infected', 'exposed', 'hospitalised', 'critical', 'dead']
master_df = pd.DataFrame(columns=column_names)

for file_name in file_list:
    if (file_name.endswith('.csv')):
        file_type = 1 if (len(file_name.split('_'))==2) else 0
        if (file_type):
            print ('My data file...')
            '''
            df = pd.read_csv(data_dir+file_name, header=None)
            df.columns = ['timestep', 'ward_no', 'infected', 'affected', 'hospitalised', 'critical', 'dead']
            print (df)
            '''
        else:
            print ('My data all together file...')
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
    ax = sns.lineplot(x='timestep', y=val, data=master_df, ci=95)
    ax.set_title('Covid-19 Simulation \nNum '+plot_title[i]+' per 100,000', weight='bold')
    ax.set_xlabel('Days')
    ax.set_ylabel('Num '+plot_title[i]+' per 100,000')
    ax.legend(labels=['No Intervention'], loc=2, fontsize='12')
    ax.figure.savefig(result_dir+val+'.png')
