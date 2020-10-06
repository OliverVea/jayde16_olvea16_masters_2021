from jaolma.gis.wfs import WFS, Filter
from jaolma.properties import Properties
from jaolma.utility.csv import CSV

wfs = WFS('https://services.datafordeler.dk/GeoDanmarkVektor/GeoDanmark60_NOHIST_GML3/1.0.0/WFS?', 
    username='VCSWRCSUKZ',
    password='hrN9aTirUg5c!np',
    version='1.1.0',
    getCapabilitiesFilename='files/capabilities_geodanmark.xml')

typenames = [
    'Bygning',
    'Broenddaeksel',
    'Mast',
    'Hegn',
    'Soe',
    'KratBevoksning',
    'Trae',
    'Nedloebsrist',
    'Chikane',
    'Vandloebskant',
    'Helle',
    'Skorsten',
    'Jernbane',
    'Bassin',
]

for area, center in zip(Properties.areas.keys(), Properties.areas.values()):
    center.to_srs(Properties.default_srs)

    n = 0
    content = []
    for typename in typenames:
        features = wfs.get_features(
            srs=Properties.default_srs, 
            typename=typename, 
            filter=Filter.radius(center, radius=100))

        geometries = [';'.join([feature.tag] + [','.join([str(x), str(y)]) for x, y in zip(feature.x(enforce_list=True), feature.y(enforce_list=True))]) for feature in features]
        
        content += [{'#': n + i, 
            'id': feature['id.lokalId'], 
            'name': typename,
            'description': typename, 
            'geometry': f'"{geometry}"'} 
            for i, (feature, geometry) in enumerate(zip(features, geometries))]

        n += len(features)

    CSV.create_file(f'files/area_data/{area}_geodanmark.csv', delimiter=',', header=['#', 'id', 'name', 'description', 'geometry'], content=content, types=['int', 'int', 'str', 'str', 'str'])