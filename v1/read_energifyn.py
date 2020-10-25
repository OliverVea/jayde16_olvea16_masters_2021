from jaolma.gis.wfs import WFS, Filter
from jaolma.properties import Properties
from jaolma.utility.csv import CSV

servicename = 'energifyn'
service = Properties.services['wfs'][servicename]

wfs = WFS(service['url'], 
    version=service['version'])

typenames = [typename for typename in Properties.feature_properties if 'origin' in Properties.feature_properties[typename] and Properties.feature_properties[typename]['origin'] == servicename]

for area, center in zip(Properties.areas.keys(), Properties.areas.values()):
    center.to_srs(Properties.default_srs)

    n = 0
    content = []
    for typename in typenames:
        center.to_srs('EPSG:4326')
        bbox = Filter.bbox(center=center, width=110, height=110)
        features = wfs.get_features(
            srs='EPSG:4326', 
            typename=typename,
            reverse_x_y=True)

        features.to_srs(Properties.default_srs)
        center.to_srs(Properties.default_srs)
        features = features.filter(lambda feature: feature.dist(center) <= 100)

        geometries = [';'.join([feature.tag] + [','.join([str(x), str(y)]) for x, y in zip(feature.x(enforce_list=True), feature.y(enforce_list=True))]) for feature in features]
        
        descriptions = {
            'TL740798': (lambda feature: f'{Properties.feature_properties["TL740798"]["label"]} h:{feature["lyspunktshoejde"]}'),
            'TL740800': (lambda feature: Properties.feature_properties['TL740800']['label']),
        }

        for feature in features:
            print(feature.attributes.keys())

        content += [{'#': n + i, 
            'id': feature['fid'].split(';')[-1], 
            'name': typename,
            'description': descriptions[typename](feature), 
            'geometry': f'"{geometry}"'} 
            for i, (feature, geometry) in enumerate(zip(features, geometries))]

        n += len(features)

    CSV.create_file(f'files/area_data/{area}_{servicename}.csv', delimiter=',', header=['#', 'id', 'name', 'description', 'geometry'], content=content, types=['int', 'int', 'str', 'str', 'str'])