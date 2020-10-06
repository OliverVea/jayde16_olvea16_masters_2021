from jaolma.gis.wfs import WFS, Filter
from jaolma.properties import Properties
from jaolma.utility.csv import CSV

wfs = WFS('https://services.drift.kortinfo.net/kortinfo/services/Wfs.ashx?Site=Odense&Page=Kortopslag',
        version='1.0.0',
        getCapabilitiesFilename='files/capabilities_kortopslag.xml')

typenames = [
        #'TL695099',         # Buildings
        #'TL965167',         # Road wells
        'L418883_421469',   # Park trees
        #'L167365_421559',   # Park points
]

for area, center in zip(Properties.areas.keys(), Properties.areas.values()):
    center.to_srs(Properties.default_srs)

    n = 0
    content = []
    for typename in typenames:
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

    CSV.create_file(f'files/area_data/{area}_kortopslag.csv', delimiter=',', header=['#', 'id', 'name', 'description', 'geometry'], content=content, types=['int', 'int', 'str', 'str', 'str'])