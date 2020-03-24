from datetime import datetime
import json
import os
import pandas as pd
from prepare_visualization_data import gen_and_save_vis_data

timeseries_file = './Data/my_data_all_together.csv'
last_file_change_time = os.path.getctime(timeseries_file)
vis_data_gen_time_file = './Data/vis_data_gen_time.csv'
vis_data_file = './Data/vis_data.csv'

if os.path.isfile(vis_data_gen_time_file):
    vis_data_gen_time = pd.read_csv(vis_data_gen_time_file, header=0)
else:
    vis_data_gen_time = pd.DataFrame({'gen_time': [0.0]})

last_vis_data_gen_time = vis_data_gen_time['gen_time'][0]

if (last_vis_data_gen_time!=last_file_change_time):
    print (vis_data_gen_time_file, ' file was changed at: ', datetime.fromtimestamp(int(last_file_change_time)).strftime('%Y-%m-%d %H:%M:%S'))
    print ('Updating visualization data...')
    ward_file = open('../staticInst/data/base/bangalore/city.geojson', 'r')
    ward_data = json.load(ward_file)

    timeseries_data = pd.read_csv(timeseries_file, header=None)
    timeseries_data.columns = ['timestep', 'ward_no', 'infected', 'affected', 'hospitalised','critical','dead']
    vis_data_gen_time['gen_time'][0] = last_file_change_time

    gen_and_save_vis_data(ward_data, timeseries_data)
    vis_data_gen_time.to_csv('./Data/vis_data_gen_time.csv', index=False)
    print ('Update finished...')

elif not (os.path.isfile(vis_data_file)):
    print ('Making visualization data for the first time... ')
    ward_file = open('../staticInst/data/base/bangalore/city.geojson', 'r')
    ward_data = json.load(ward_file)

    timeseries_data = pd.read_csv(timeseries_file, header=None)
    timeseries_data.columns = ['timestep', 'ward_no', 'infected', 'affected', 'hospitalised','critical','dead']
    vis_data_gen_time['gen_time'][0] = last_file_change_time

    gen_and_save_vis_data(ward_data, timeseries_data)
    vis_data_gen_time.to_csv('./Data/vis_data_gen_time.csv', index=False)
    print ('Update finished...')

else:
    print (vis_data_gen_time_file, ' file was not changed...')
    print ('No updates were performed...')
