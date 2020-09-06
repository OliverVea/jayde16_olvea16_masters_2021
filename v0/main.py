from wfs import WMTS, WFS, WFS_Feature
from get_gps import GPSConnection
from maps import MPL_Map
from utility import printe

use_real_coords = False

typenames = ['Mast', 'Nedloebsrist', 'Skorsten', 'Telemast', 'Trae', 'Broenddaeksel']
colors = ['#FF0000', '#0000FF', '#FFFF00', '#FF00FF', '#00FF00', 'grey']

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
    conn = GPSConnection(address='10.147.18.175', port=7789)
    coords = conn.get_coords(timeout=2).to_srs('EPSG:3857')
except:
    printe(f'Could not get coordinates. Using default instead.')
    coords = WFS_Feature(tag='GPS', geometry=(55.369837, 10.431700), default_srs='EPSG:4326').to_srs('EPSG:3857')

m = MPL_Map(coordinates = coords, wmts=wmts, wfs=wfs, wfs_typenames=typenames, wfs_colors=colors)

