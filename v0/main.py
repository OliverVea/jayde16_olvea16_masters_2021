if __name__ == '__main__':
    from wfs import WFS, Feature, Point
    from wmts import WMTS
    from gps import GPSConnection
    from maps import MPL_Map
    from utility import printe, prints, set_verbose

    typenames = ['Mast', 'Nedloebsrist', 'Skorsten', 'Telemast', 'Trae', 'Broenddaeksel']
    colors = ['#FF0000', '#0000FF', '#FFFF00', '#FF00FF', '#00FF00', 'grey']

    gps_ip = '10.147.18.175'

    timeout = 2 # seconds

    wfs = WFS('https://services.datafordeler.dk/GeoDanmarkVektor/GeoDanmark60_NOHIST_GML3/1.0.0/WFS?', 
        username='VCSWRCSUKZ',
        password='hrN9aTirUg5c!np',
        version='1.1.0')

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
        coords = Feature(tag='GPS', geometry=(55.369837, 10.431700), default_srs='EPSG:4326')
        prints(f'Could not get coordinates. Using default instead.')
    
    coords.to_srs('EPSG:3857')

    m = MPL_Map(coordinates = coords, wmts=wmts, wfs=wfs, wfs_typenames=typenames, wfs_colors=colors)

