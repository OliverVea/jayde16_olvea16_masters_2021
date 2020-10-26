from jaolma.gis.wfs import Feature
from jaolma.properties import Properties
from jaolma.utility.utility import prints
from jaolma.utility.csv import CSV

import pandas as pd

servicename = 'samaqua'
typename = 'water_node'

node_type_code = CSV('files/samaqua/node_type_code.csv', delimiter=';')
d_knudekode_beskrivelse = {row['KnudeKode']: row['Beskrivelse'] for row in node_type_code.load()}

origin_code = CSV('files/samaqua/origin_code.csv', delimiter=';')
d_coordorigincode_beskrivelse = {row['CoordOriginCode']: row['Beskrivelse'] for row in origin_code.load()}

owner_id = CSV('files/samaqua/owner_id.csv', delimiter=';')
d_oid_ownershipname = {row['OwnerID']: row['OwnershipName'] for row in owner_id.load()}

origin_journal = CSV('files/samaqua/origin_journal.csv', delimiter=';')
d_oid_journal = {row['ObjectID']: row for row in origin_journal.load()}

nodes = CSV('files/samaqua/node_cover.csv', delimiter=';').load()

for area in Properties.areas:
    center = Properties.areas[area].as_srs(srs='EPSG:25832')

    rows = []    
    for i, row in enumerate(nodes):
        if 'NULL' in [row['X_Node'], row['Y_Node']]:
            continue

        geometry = (float(row['X_Node']), float(row['Y_Node']))
        feature = Feature(geometry, Properties.default_srs, 'Point', {key: val for key, val in zip(row.keys(), row.values()) if not key in ['X_Node', 'Y_Node'] and val != 'NULL'})
        
        if feature.dist(center) > Properties.radius:
            continue

        data = {}
        data['typename'] = typename
        data['id'] = feature['FeatureGUID']
        data['label'] = Properties.feature_properties[typename]['label']
        data['geometry'] = f'{feature.tag};{list(feature.x(enforce_list=True))},{list(feature.y(enforce_list=True))}'
        data['service'] = servicename

        if 'OwnerID' in feature.attributes and feature['OwnerID'] in d_oid_ownershipname:
            data['actor'] = d_oid_ownershipname[feature['OwnerID']]

        if 'NodeType' in feature.attributes and feature['NodeType'] in d_knudekode_beskrivelse:
            data['description'] = d_knudekode_beskrivelse[feature['NodeType']]

        optionals = {
            'date': 'Node_DateModified', 
            'name': 'NodeName', 
            'cover_level': 'CoverLevel'}

        for key, val in zip(optionals.keys(), optionals.values()):
            if val in feature.attributes:
                data[key] = feature[val]
                
        rows.append(pd.DataFrame([data.values()], columns=data.keys()))

    dataframe = pd.DataFrame()
    if len(rows) > 0:
        dataframe = pd.concat(rows, ignore_index=True)

    dataframe.to_csv(f'files/areas/{servicename}_{area}_{len(dataframe)}.csv')
    prints(f'Found {len(dataframe)} features for area {area}.', tag='Main')