if __name__ == '__main__':
    from wfs import WFS, Feature, Point
    from wmts import WMTS
    from gps import GPSConnection
    from maps import MPL_Map
    from utility import printe, prints, set_verbose

    #set_verbose(tag_blacklist=['MPL_Map'])

    #typenames = ['Mast', 'Nedloebsrist', 'Skorsten', 'Telemast', 'Trae', 'Broenddaeksel', 'Bygning']
    #colors = ['#FFFFFF', '#0000FF', '#FFFF00', '#FF00FF', '#10AA09', '#000000', '#FF0000']

    typenames = []
    with open('categories.txt', 'r') as f:
        for line in f:
            typenames.append(line[:-1])

    #typenames = ['KratBevoksning']
    colors = None
    radius = None
    init_tile_matrix = 12

    gps_ip = '10.147.18.175'

    timeout = 2 # seconds

    wfs = WFS('https://services.datafordeler.dk/GeoDanmarkVektor/GeoDanmark60_NOHIST_GML3/1.0.0/WFS?', 
        username='VCSWRCSUKZ',
        password='hrN9aTirUg5c!np',
        version='1.1.0')

    #wfs.get_features(srs='EPSG:3857', typename='Systemlinje', max_features=1)

    wmts = WMTS('https://services.datafordeler.dk/GeoDanmarkOrto/orto_foraar_wmts/1.0.0/WMTS?',
        username='VCSWRCSUKZ',
        password='hrN9aTirUg5c!np',
        layer='orto_foraar_wmts',
        tile_matrix_set='KortforsyningTilingDK')

    try:
        conn = GPSConnection(address=gps_ip, port=7789)
        coords = conn.get_coords(timeout=timeout)
    except:
        pass

    if coords != None:
        prints(f'Got authentic coordinates from gps.')
    else:
        coords = Point(geometry=(55.369837, 10.431700), srs='EPSG:4326')
        prints(f'Could not get coordinates. Using default instead.')
    
    coords.to_srs('EPSG:3857')

    m = MPL_Map(coordinates = coords, wmts=wmts, wfs=wfs, wfs_typenames=typenames, wfs_colors=colors, init_tile_matrix=init_tile_matrix, radius=radius)
