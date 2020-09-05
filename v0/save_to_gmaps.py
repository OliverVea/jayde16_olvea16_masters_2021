from utility import prints
from wfs import WFS, WFS_Filter, WFS_Feature

import gmplot

typenames = ['Mast', 'Nedloebsrist', 'Skorsten', 'Telemast', 'Trae', 'Broenddaeksel']
colors = ['#FF0000', '#0000FF', '#FFFF00', '#FF00FF', '#00FF00', 'grey']

gmap3 = gmplot.GoogleMapPlotter(55.369837, 10.431700, 16, apikey='AIzaSyA0y2iofkkWlv8v5KnAYpkW8KBRopsN8Ag')

wfs = WFS('https://services.datafordeler.dk/GeoDanmarkVektor/GeoDanmark60_NOHIST_GML3/1.0.0/WFS?', 
    username='VCSWRCSUKZ',
    password='hrN9aTirUg5c!np',
    version='1.1.0')

coords = WFS_Feature(tag='GPS', geometry=(55.369837, 10.431700), default_srs='EPSG:4326').to_srs('EPSG:3857')
wfs_filter = WFS_Filter.radius(None, center=coords, radius=50, property='geometri')

for typename, color in zip(typenames, colors):
    prints(f'Requesting features of type {typename}.')
    features = wfs.get_features(typename=typename, srs_name='EPSG:3857', max_features=None, filter=wfs_filter)

    prints('Transforming points...')
    pts = [feature.pos('EPSG:4326') for feature in features.values()]
    pts_lat, pts_lon = [pt[0] for pt in pts], [pt[1] for pt in pts]

    prints('Plotting points.')
    gmap3.scatter(pts_lat, pts_lon,size=30, color=color)

gmap3.draw('map.html')

prints('Map has been drawn.')