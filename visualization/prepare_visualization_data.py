#Copyright [2020] [Indian Institute of Science, Bangalore]
#SPDX-License-Identifier: Apache-2.0

from datetime import datetime, timedelta 
import geojson as gjsn
import json
import numpy as np
import pandas as pd
from tqdm import trange

def verify_count(val):
    if (len(val)):
        return (int(val))
    else:
        return (0)

def gen_and_save_vis_data(ward_info, timeseries_info):
    OBJECT_ID = []
    WARD_NO = []
    WARD_NAME = []
    LAT = []
    LON = []
    INFECTED = []
    AFFECTED = []
    HOSPITALISED = []
    CRITICAL = []
    DEAD = []
    TIMESTAMP = []
    GEOMETRY = []

    NUM_TIMESTEPS = int(len(timeseries_info)/198)

    init_date = datetime.strptime('2020/01/01 00:01', '%Y/%m/%d %H:%M')

    for i in range(NUM_TIMESTEPS):
        for feature in ward_info['features']:
            fm_date = init_date + timedelta(days=i)
            OBJECT_ID.append(feature['properties']['OBJECTID'])
            WARD_NO.append(feature['properties']['WARD_NO'])
            WARD_NAME.append(feature['properties']['WARD_NAME'])
            LAT.append(feature['properties']['LAT'])
            LON.append(feature['properties']['LON'])
            condition_1 = (timeseries_info['timestep']==i)
            condition_2 = (timeseries_info['ward_no']==feature['properties']['WARD_NO'])
            filtered_row = timeseries_info[condition_1 & condition_2]
            INFECTED.append(verify_count(filtered_row['infected']))
            AFFECTED.append(verify_count(filtered_row['affected']))
            HOSPITALISED.append(verify_count(filtered_row['hospitalised']))
            CRITICAL.append(verify_count(filtered_row['critical']))
            DEAD.append(verify_count(filtered_row['dead']))
            TIMESTAMP.append(datetime.strftime(fm_date, '%Y/%m/%d %H:%M'))
            GEOMETRY.append('{"type": "Polygon", "coordinates": ' + str(feature['geometry']['coordinates'])[1:-1]+'}' )

    df = pd.DataFrame({
        'ObjectID': OBJECT_ID,
        'WardNo': WARD_NO,
        'WardName': WARD_NAME,
        'Latitude': LAT,
        'Longitude': LON,
        'Infected': INFECTED,
        'Affected': AFFECTED,
        'Hospitalised': HOSPITALISED,
        'Critical': CRITICAL,
        'Dead': DEAD,
        'Geometry': GEOMETRY,
        'TimeStamp': TIMESTAMP
    })

    df.to_csv('./Data/vis_data.csv', index=False)

