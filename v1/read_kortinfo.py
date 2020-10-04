from jaolma.gis.wfs import WFS, Filter
from jaolma.properties import Properties
from jaolma.utility.csv import CSV

wfs = WFS('https://services.drift.kortinfo.net/kortinfo/services/Wfs.ashx?Site=Odense&Page=Kortopslag',
        version='1.0.0')

typenames = [
        'TL695099',         # Buildings
        'TL965167',         # Road wells
        'L418883_421469',   # Park trees
        'L167365_421559',   # Park points
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
            'description': typename, 
            'geometry': f'"{geometry}"'} 
            for i, (feature, geometry) in enumerate(zip(features, geometries))]

        n += len(features)

    CSV.create_file(f'files/area_data/{area}_kortinfo.csv', delimiter=',', header=['#', 'id', 'description', 'geometry'], content=content, types=['int', 'int', 'str', 'str'])