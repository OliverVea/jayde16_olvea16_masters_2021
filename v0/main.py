from wfs import WMTS, WFS, WFS_Filter
from utility import prints
from get_gps import GPSConnection

from PIL import Image, ImageDraw

wmts = WMTS('https://services.datafordeler.dk/GeoDanmarkOrto/orto_foraar_wmts/1.0.0/WMTS?',
    username='VCSWRCSUKZ',
    password='hrN9aTirUg5c!np',
    layer='orto_foraar_wmts',
    tile_matrix_set='KortforsyningTilingDK')

conn = GPSConnection(address='10.147.18.175', port=7789)
coords = conn.get_coords().to_srs('EPSG:3857')

m = wmts.get_map(style='default', tile_matrix=13, center=coords)

draw = ImageDraw.Draw(m.image)

wfs_filter = WFS_Filter.radius(None, center=coords, radius=50, property='geometri')
print(wfs_filter)

typenames = ['Mast', 'Nedloebsrist', 'Skorsten', 'Telemast', 'Trae', 'Broenddaeksel']
colors = ['#FF0000', '#0000FF', '#FFFF00', '#FF00FF', '#00FF00', 'grey']

wfs = WFS('https://services.datafordeler.dk/GeoDanmarkVektor/GeoDanmark60_NOHIST_GML3/1.0.0/WFS?', 
    username='VCSWRCSUKZ',
    password='hrN9aTirUg5c!np',
    version='1.1.0')

for typename, color in zip(typenames[1:2], colors):
    prints(f'Requesting features of type {typename}.')
    features = wfs.get_features(typename=typename, srs_name=m.center.default_srs, max_features=None, filter=wfs_filter, as_list=True)

    prints('Plotting points.')
    r = 2
    for ft in features[:1]:
        x, y = m.coord_to_pixels(ft)
        xy = (x - r, y - r, x + r, y + r)
        draw.ellipse(xy, fill=color)

prints('Map has been drawn.')

m.image.save('map.png')
m.image.show()