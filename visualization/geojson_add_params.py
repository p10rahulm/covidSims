from datetime import datetime, timedelta 
import geojson as gjsn
import json
import numpy as np
import pandas as pd

ward_file = open('../staticInst/data/banglore_citymap.geojson', 'r')
ward_data = json.load(ward_file)

OBJECT_ID = []
WARD_NO = []
WARD_NAME = []
LAT = []
LON = []
COUNT = []
TIMESTAMP = []
GEOMETRY = []

NUM_TIMESTEPS = 95

for feature in ward_data['features']:
    for i in range(NUM_TIMESTEPS):
        minutes = (i*15) % 60
        hours = int(np.floor((i*15) / 60))
        OBJECT_ID.append(feature['properties']['OBJECTID'])
        WARD_NO.append(feature['properties']['WARD_NO'])
        WARD_NAME.append(feature['properties']['WARD_NAME'])
        LAT.append(feature['properties']['LAT'])
        LON.append(feature['properties']['LON'])
        COUNT.append(np.random.randint(0, 100))
        TIMESTAMP.append('2020/01/01 '+str(hours)+':'+str(minutes))
        GEOMETRY.append('{"type": "Polygon", "coordinates": ' + str(feature['geometry']['coordinates'])[1:-1]+'}' )

df = pd.DataFrame({
    'ObjectID': OBJECT_ID,
    'WardNo': WARD_NO,
    'WardName': WARD_NAME,
    'Latitude': LAT,
    'Longitude': LON,
    'Count': COUNT,
    'Geometry': GEOMETRY,
    'TimeStamp': TIMESTAMP
})

df.to_csv('./kepler_data.csv', index=False)