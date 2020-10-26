from jaolma.gis.wfs import WFS, Filter
from jaolma.properties import Properties
from jaolma.utility.utility import prints, set_verbose

import pandas as pd

set_verbose(tag_blacklist=['WFS'])

servicename = 'geodanmark'
service = Properties.services['wfs'][servicename]

wfs = WFS(service['url'], version=service['version'], username=service['username'], password=service['password'])

typenames = [typename for typename in Properties.feature_properties if 'origin' in Properties.feature_properties[typename] and Properties.feature_properties[typename]['origin'] == servicename]

prints(f'Retrieving features: {", ".join([Properties.feature_properties[typename]["label"] + " (" + typename + ")" for typename in typenames])}', tag='Main')
prints(f'In areas: {", ".join(Properties.areas.keys())}', tag='Main')

for area, center in zip(Properties.areas.keys(), Properties.areas.values()):
    center.to_srs(Properties.default_srs)

    frames = []

    for typename in typenames:
        bbox = Filter.bbox(center=center, width=Properties.radius, height=Properties.radius)

        features = wfs.get_features(
            srs=Properties.default_srs, 
            typename=typename, 
            bbox=bbox)

        features = features.filter(lambda feature: feature.dist(center) <= Properties.radius)
        
        rows = {}    
        for feature in features:
            data = {}
            data['id'] = feature['id.lokalId']
            data['label'] = Properties.feature_properties[typename]['label']
            data['geometry'] = f'{feature.tag};{list(feature.x(enforce_list=True))},{list(feature.y(enforce_list=True))}'

            optionals = {
                'actor': 'registreringsaktoer',
                'date': 'registreringFra',
                'horizontal_precision': 'planNoejagtighed',
                'vertical_precision': 'vertikalNoejagtighed'}

            for key, val in zip(optionals.keys(), optionals.values()):
                if val in feature.attributes:
                    data[key] = feature[val]

            for key, value in zip(data.keys(), data.values()):
                rows.setdefault(key, []).append(value)

        frames.append(pd.DataFrame(rows))

    dataframe = pd.concat(frames, ignore_index=True)
    dataframe.to_csv(f'files/area_data/{servicename}_{area}.csv')
    prints(f'Found {len(dataframe)} features for area {area}.', tag='Main')