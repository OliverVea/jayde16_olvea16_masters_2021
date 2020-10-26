from jaolma.gis.wfs import Feature, Collection
from jaolma.properties import Properties
from jaolma.utility.utility import prints

import pandas as pd
import json
from datetime import datetime

servicename = 'fjernvarme'
typename = 'heating_cover'

prints(f'Retrieving features from fjernvarme.', tag='Main')
prints(f'In areas: {", ".join(Properties.areas.keys())}', tag='Main')

for area in Properties.areas:
    center = Properties.areas[area].as_srs(srs='EPSG:25832')

    with open("files/fjernvarme/casings.json", "r") as f:
        input_data = json.load(f)

    features = [Feature(list(d['geometry'].values()), Properties.default_srs, 'Point', d['attributes']) for d in input_data['features']]

    features = Collection(servicename, 'Point', features, Properties.default_srs)

    features = features.filter(lambda feature: feature.dist(center) <= Properties.radius)

    rows = {}
    for feature in features:
        data = {}
        data['typename'] = typename
        data['id'] = feature['GlobalID']
        data['label'] = Properties.feature_properties[typename]['label']
        data['geometry'] = f'{feature.tag};{list(feature.x(enforce_list=True))},{list(feature.y(enforce_list=True))},{list(feature.z(enforce_list=True))}'
        data['service'] = servicename
        data['diameter_cm'] = feature['CAPCODE']
        data['shape'] = feature['CASINGFORM']
        data['n_caps'] = feature['NUMCAPS']
        data['rotation'] = feature['ROTATION']
        data['owner'] = feature['OWNER']
        data['date'] = datetime.fromtimestamp(int(feature['EDITED']) / 1e3).strftime('%Y-%m-%dT%H:%M:%S')

        for key, value in zip(data.keys(), data.values()):
            rows.setdefault(key, []).append(value)

    dataframe = pd.DataFrame(rows)
    dataframe.to_csv(f'files/areas/{servicename}_{area}_{len(dataframe)}.csv')
    prints(f'Found {len(dataframe)} features for area {area}.', tag='Main')