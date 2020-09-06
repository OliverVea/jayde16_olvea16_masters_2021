from wfs import WMTS, WFS, WFS_Filter, WFS_Feature
from utility import prints
from get_gps import GPSConnection

from PIL import Image, ImageDraw

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent

use_real_coord = False

wmts = WMTS('https://services.datafordeler.dk/GeoDanmarkOrto/orto_foraar_wmts/1.0.0/WMTS?',
    username='VCSWRCSUKZ',
    password='hrN9aTirUg5c!np',
    layer='orto_foraar_wmts',
    tile_matrix_set='KortforsyningTilingDK')

conn = GPSConnection(address='10.147.18.175', port=7789)

if use_real_coord: coords = conn.get_coords().to_srs('EPSG:3857')
else: coords = WFS_Feature(tag='GPS', geometry=(55.369837, 10.431700), default_srs='EPSG:4326').to_srs('EPSG:3857')

coords = coords.to_srs('urn:ogc:def:crs:EPSG:6.3:25832')

typenames = ['Mast', 'Nedloebsrist', 'Skorsten', 'Telemast', 'Trae', 'Broenddaeksel']
colors = ['#FF0000', '#0000FF', '#FFFF00', '#FF00FF', '#00FF00', 'grey']

tile_matrix = 15
cached_points = {}


points_dict = {}
def scroll(event):

    global tile_matrix

    if event.button == 'up' and tile_matrix < 15:
        print('scrolled: up')
        tile_matrix = tile_matrix + 1
    elif event.button == 'down' and tile_matrix > 10:
        print('scrolled: down')
        tile_matrix = tile_matrix - 1
    print('tile_matrix is:', tile_matrix)

    plt.clf()

    m = wmts.get_map(style='default', tile_matrix=tile_matrix, center=coords)

    wfs_filter = WFS_Filter.radius(center=coords, radius=1080 / m.dpm * 0.5, property='geometri')
    print(wfs_filter)

    wfs = WFS('https://services.datafordeler.dk/GeoDanmarkVektor/GeoDanmark60_NOHIST_GML3/1.0.0/WFS?', 
        username='VCSWRCSUKZ',
        password='hrN9aTirUg5c!np',
        version='1.1.0')

    typepoints = []
    for typename, color in zip(typenames, colors):
        if (tile_matrix, typename) not in cached_points:
            prints(f'Requesting features of type {typename}.')
            features = wfs.get_features(typename=typename, srs_name=m.center.default_srs, max_features=None, filter=wfs_filter, as_list=True)

            prints('Plotting points.')
            points = [[],[]]
            for ft in features:
                x, y = m.coord_to_pixels(ft, srs='urn:ogc:def:crs:EPSG:6.3:25832')
                points[0].append(x)
                points[1].append(y)
            cached_points[(tile_matrix, typename)] = points
        
        points = cached_points[(tile_matrix, typename)]

        if len(points[0]) > 0:
            typepoints.append(plt.plot(points[0], points[1], '*', color=color, label=typename))

    img = m.image
    plt.imshow(img, extent=[-1920 / m.dpm * 0.5, 1920 / m.dpm * 0.5, 1080 / m.dpm * 0.5, -1080 / m.dpm * 0.5])

    plt.margins(0,0)
    leg = plt.legend()

    for legpoint, origpoints in zip(leg.get_lines(), typepoints):
        legpoint.set_picker(5)  # 5 pts tolerance
        points_dict[legpoint] = origpoints[0]

    plt.draw()
    prints('Map has been drawn.')

def onpick(event):
    legpoint = event.artist
    origpoints = points_dict[legpoint]
    vis = not origpoints.get_visible()
    origpoints.set_visible(vis)
    # Change the alpha on the line in the legend so we can see what lines
    # have been toggled
    if vis:
        legpoint.set_alpha(1.0)
    else:
        legpoint.set_alpha(0.2)
    fig.canvas.draw()

fig = plt.figure()


scroll(MouseEvent('',fig.canvas,0,0))

fig.canvas.mpl_connect('scroll_event', scroll)
fig.canvas.mpl_connect('pick_event', onpick)


plt.show()
