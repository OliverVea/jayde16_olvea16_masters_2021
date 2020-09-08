if __name__ == '__main__':
    from wfs import WFS, Feature, Filter
    from wmts import WMTS
    from gps import GPSConnection
    from maps import MPL_Map
    from utility import printe, prints, set_verbose

    #set_verbose(status=False, error=False)

    typenames = []
    with open('filtered_categories.txt', 'r') as f:
        for line in f:
            typenames.append(line[:-1])

    colors = None
    radius = None
    init_tile_matrix = 13
    r = 70

    wfs = WFS('https://services.datafordeler.dk/GeoDanmarkVektor/GeoDanmark60_NOHIST_GML3/1.0.0/WFS?', 
        username='VCSWRCSUKZ',
        password='hrN9aTirUg5c!np',
        version='1.1.0')

    markers = {'suburb': (55.3761308,10.3860752), 'university_parking': (55.3685818,10.4317584), 'university_campus': (55.3689566,10.4281531), 'downtown': (55.3947509,10.3833619), 'harbor': (55.4084239,10.3813301), 'park': (55.391766,10.3821373)}
    coords = [Feature(tag=key, geometry=value, srs='EPSG:4326', attributes={}) for key, value in zip(markers.keys(), markers.values())]

    wmts = WMTS('https://services.datafordeler.dk/GeoDanmarkOrto/orto_foraar_wmts/1.0.0/WMTS?',
        username='VCSWRCSUKZ',
        password='hrN9aTirUg5c!np',
        layer='orto_foraar_wmts',
        tile_matrix_set='KortforsyningTilingDK')

    for center in coords:  
        center.to_srs('EPSG:3857')  
        filter = Filter.radius(center=center, radius=r)
        m = MPL_Map(coordinates=center, wmts=wmts, wfs=wfs, wfs_typenames=typenames, wfs_colors=colors, init_tile_matrix=init_tile_matrix, radius=r)
