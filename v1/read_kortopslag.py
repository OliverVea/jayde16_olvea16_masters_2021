from jaolma.gis.wfs import WFS, Filter
from jaolma.properties import Properties
from jaolma.utility.csv import CSV
from jaolma.utility.utility import prints

servicename = 'kortopslag'
service = Properties.services['wfs'][servicename]

wfs = WFS(service['url'], 
    version=service['version'])

typenames = [typename for typename in Properties.feature_properties if 'origin' in Properties.feature_properties[typename] and Properties.feature_properties[typename]['origin'] == servicename]

for area, center in zip(Properties.areas.keys(), Properties.areas.values()):
    prints(f'Area: {area}.')

    center.to_srs(Properties.default_srs)

    n = 0
    content = []
    for typename in typenames:
        prints(f'Typename: {typename}, Label: {Properties.feature_properties[typename]["label"]}.')
        bbox = Filter.bbox(center=center, width=110, height=110)
        features = wfs.get_features(
            srs=Properties.default_srs, 
            typename=typename, 
            bbox=bbox)

        features = features.filter(lambda feature: feature.dist(center) <= 100)

        geometries = [';'.join([feature.tag] + [','.join([str(x), str(y)]) for x, y in zip(feature.x(enforce_list=True), feature.y(enforce_list=True))]) for feature in features]
        
        content += [{'#': n + i, 
            'id': feature['objekt_id'], 
            'name': typename,
            'description': '_'.join([feature[key] for key in ['hovedelement_tekst', 'element_tekst', 'underelement_tekst']]), 
            'geometry': f'"{geometry}"'} 
            for i, (feature, geometry) in enumerate(zip(features, geometries))]

        n += len(features)

    CSV.create_file(f'files/area_data/{area}_{servicename}.csv', delimiter=',', header=['#', 'id', 'name', 'description', 'geometry'], content=content, types=['int', 'str', 'str', 'str', 'str'])