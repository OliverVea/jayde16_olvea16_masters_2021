from jaolma.gis.wfs import Feature, Collection
from jaolma.properties import Properties
from jaolma.utility.utility import prints

import pandas as pd
from datetime import datetime

import json
import os

servicename = 'gt'

files = os.listdir('files/areas/')
for file in files:
    if servicename in file:
        os.remove('files/areas/' + file)

prints(f'Retrieving features from ground truth.', tag='Main')
prints(f'In areas: {", ".join(Properties.areas.keys())}', tag='Main')

for area in ['suburb', 'park']:#'sdu', 'harbor', 'park']:#Properties.areas:
    center = Properties.areas[area].as_srs(srs='EPSG:25832')

    input_data = pd.read_csv(f'files/ground_truth/epsg_25832/gt_{area}.csv', dtype=str)

    features = []
    for i, row in input_data.iterrows():
        row_as_dict = row.to_dict()
        del row_as_dict['x']
        del row_as_dict['y']
        features.append(Feature((float(row.x),float(row.y)), srs='EPSG:25832', tag='Point', attributes=row_as_dict))

    features = Collection(servicename, 'Point', features, 'EPSG:25832')

    #features.to_srs(Properties.default_srs)

    features = features.filter(lambda feature: feature.dist(center) <= Properties.outer_radius)
    
    rows = {}
    for feature in features:
        data = feature.attributes
        data['geometry'] = f'{feature.tag};{list(feature.x(enforce_list=True))},{list(feature.y(enforce_list=True))}'
        data['label'] = feature['typename']
        data['id'] = feature['ID']
        del data['ID']
        for key, value in zip(data.keys(), data.values()):
            rows.setdefault(key, []).append(value)
    
    dataframe = pd.DataFrame(rows)
    dataframe.to_csv(f'files/areas/{servicename}_{area}_{len(dataframe)}.csv')
    prints(f'Found {len(dataframe)} features for area {area}.', tag='Main')