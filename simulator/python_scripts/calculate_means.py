#Copyright [2020] [Indian Institute of Science, Bangalore]
#SPDX-License-Identifier: Apache-2.0

import numpy as np
import os
import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt

def calculate_means(data_dir, result_dir):

    file_list = os.listdir(data_dir)

    if not (os.path.exists(result_dir)):
        os.mkdir(result_dir)    
    
    print (data_dir)
    column_names = ['timestep', 'affected', 'recovered', 'infected', 'exposed', 'hospitalised', 'critical', 'dead', 'lambda H', 'lambda W', 'lambda C']
    master_df = pd.DataFrame(columns=column_names)

    for file_name in file_list:
        if (file_name.endswith('.csv')):
            file_type = 1 if (len(file_name.split('_'))==3) else 0
            if (file_type):
                '''
                df = pd.read_csv(data_dir+file_name, header=None)
                df.columns = ['timestep', 'ward_no', 'infected', 'affected', 'hospitalised', 'critical', 'dead', 'lambda H', 'lambda W', 'lambda C']
                print (df)
                '''
            else:
                df = pd.read_csv(data_dir+file_name, header=None)
                df.columns = ['timestep', 'affected', 'recovered', 'infected', 'exposed', 'hospitalised', 'critical', 'dead', 'lambda H', 'lambda W', 'lambda C']
                master_df = master_df.append(df)

    master_df[['timestep', 'affected', 'recovered', 'infected', 'exposed', 'hospitalised', 'critical', 'dead', 'lambda H', 'lambda W', 'lambda C']] = master_df[['timestep', 'affected', 'recovered', 'infected', 'exposed', 'hospitalised', 'critical', 'dead', 'lambda H', 'lambda W', 'lambda C']].apply(pd.to_numeric)

    plot_values = ['affected', 'recovered', 'hospitalised', 'infected', 'critical', 'dead', 'lambda H', 'lambda W', 'lambda C']
    plot_title = ['Affected (cum.)', 'Recovered (cum.)', 'Hospitalised (daily)', 'Infected (daily)', 'Critical (daily)', 'Fatalities (cum.)', 'lambda H', 'lambda W', 'lambda C']

    for i in range(len(plot_values)):
        val = plot_values[i]
        plt.figure(figsize=(13,5))
        sns.set()
        df = master_df[['timestep', val]]
        df_mean = df.groupby(['timestep']).mean()
        df_mean.to_csv(result_dir+val+'_mean.csv')
        
    return (True)

