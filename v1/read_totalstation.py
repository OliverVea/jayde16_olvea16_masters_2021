from jaolma.gis.wfs import Feature, Collection
from jaolma.properties import Properties
from jaolma.utility.utility import prints

import pandas as pd
from datetime import datetime

import json

servicename = 'totalstation'

prints(f'Retrieving features from Totalstation.', tag='Main')
prints(f'In areas: {", ".join(Properties.areas.keys())}', tag='Main')


input_data = pd.read_csv(f'files/totalstation/totalstation_all.csv')


for area in ['park', 'suburb', 'downtown']:#Properties.areas:
    center = Properties.areas[area].as_srs(srs='EPSG:25832')

    features = []
    for i, row in input_data.iterrows():
        if row['area'] == area:
            row_as_dict = row.to_dict()
            del row_as_dict['East']
            del row_as_dict['North']
            features.append(Feature((row.East,row.North), srs='EPSG:25832', tag='Point', attributes=row_as_dict))

    features = Collection(servicename, 'Point', features, 'EPSG:25832')

    features.to_srs(Properties.default_srs)

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