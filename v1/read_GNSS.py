from jaolma.gis.wfs import Feature, Collection
from jaolma.properties import Properties
from jaolma.utility.utility import prints

import pandas as pd
from datetime import datetime

import json

servicename = 'gnss'

prints(f'Retrieving features from GNSS.', tag='Main')
prints(f'In areas: {", ".join(Properties.areas.keys())}', tag='Main')

for area in ['suburb']:#Properties.areas:
    center = Properties.areas[area].as_srs(srs='EPSG:25832')

    input_data = pd.read_csv('files/GNSS/GNSS_suburb.csv')

    features = []
    for lat, lon, typename, ID, time, fix, nSat, hError, note, date in zip(input_data.lat.values, input_data.lon.values, 
                        input_data.type.values, input_data.ID.values,
                        input_data.timePretty.values, input_data.fix.values,
                        input_data.nSat.values, input_data.hError.values,
                        input_data.notes.values, input_data.date.values):
        features.append(Feature((lat,lon), srs='EPSG:4326', tag='Point', attributes={'typename': typename,
                        'ID': ID, 'time': time, 'fix': fix, 'nSat': nSat, 'hError': hError, 'note': note, 'date': date}))
    
    features = Collection(servicename, 'Point', features, 'EPSG:4326')

    features.to_srs(Properties.default_srs)

    features = features.filter(lambda feature: feature.dist(center) <= Properties.radius)

    rows = {}
    for feature in features:
        data = {}
        data['typename'] = feature['typename']
        data['id'] = feature['ID']
        data['label'] = feature['typename']
        data['geometry'] = f'{feature.tag};{list(feature.x(enforce_list=True))},{list(feature.y(enforce_list=True))}'
        data['service'] = servicename
        data['time'] = feature['time']
        data['fix'] = feature['fix']
        data['nSat'] = feature['nSat']
        data['hError'] = feature['hError']
        data['note'] = feature['note']
        data['date'] = feature['date']

        for key, value in zip(data.keys(), data.values()):
            rows.setdefault(key, []).append(value)

    dataframe = pd.DataFrame(rows)
    dataframe.to_csv(f'files/areas/{servicename}_{area}_{len(dataframe)}.csv')
    prints(f'Found {len(dataframe)} features for area {area}.', tag='Main')