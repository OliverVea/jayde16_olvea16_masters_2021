if __name__ == '__main__':
    from wfs import WFS, Feature, Filter
    from wmts import WMTS
    from gps import GPSConnection
    from maps import Map
    from utility import printe, prints, set_verbose

    #set_verbose(status=False, error=False)

    typenames = []
    with open('input/filtered_categories.txt', 'r') as f:
        for line in f:
            typenames.append(line[:-1])

    tile_matrix = 14
    r = 100

    wfs = WFS('https://services.datafordeler.dk/GeoDanmarkVektor/GeoDanmark60_NOHIST_GML3/1.0.0/WFS?', 
        username='VCSWRCSUKZ',
        password='hrN9aTirUg5c!np',
        version='1.1.0')

    markers = {'suburb': (55.3761308,10.3860752), 'university_parking': (55.3685818,10.4317584), 'downtown': (55.3947509,10.3833619), 'harbor': (55.4083756,10.3787729), 'park': (55.3916561,10.3828329)}

    markers = {key: markers[key] for key in ['downtown']}

    wmts = WMTS('https://services.datafordeler.dk/GeoDanmarkOrto/orto_foraar_wmts/1.0.0/WMTS?',
        username='VCSWRCSUKZ',
        password='hrN9aTirUg5c!np',
        layer='orto_foraar_wmts',
        tile_matrix_set='KortforsyningTilingDK')

    dpi = 300
    figsize = (8, 8)

    typenames = ['Bygning']
    
    for area, center in zip(markers.keys(), markers.values()):
        center = Feature(tag=area, geometry=center, srs='EPSG:4326', attributes={})
        center.to_srs('EPSG:3857')

        N = 0

        m = Map(center=center.as_srs('urn:ogc:def:crs:EPSG:6.3:25832'), wmts=wmts, figname=f'{area}_all', tile_matrix=tile_matrix, figsize=figsize, dpi=dpi)

        with open(f'output/_{area}_features.csv', 'w') as f:
            f.write(','.join([str(e) for e in ['area', 'feature type', 'feature name', 'id.lokalId', 'feature #']]) + '\n')

        filter = Filter.radius(center=center, radius=r)
        for typename in typenames:

            features = wfs.get_features(typename=typename, srs='EPSG:3857', filter=filter) 
            n = len(features.features)

            if n > 0:

                m.add_feature(features, label=features.tag, annotations=[N + i for i in range(n)])

                with open(f'output/_{area}_features.csv', 'a') as f:
                    f.write(','.join([area, features.type, typename, str(n)]) + '\n')

                N += n
        
        with open(f'output/_{area}_features.csv', 'a') as f:    
            f.write(','.join([area, '', 'total', str(N)]) + '\n')

        m.add_circle(center, r)
        m.show()
