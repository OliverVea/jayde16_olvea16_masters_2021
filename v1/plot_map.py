from jaolma.properties import Properties
from jaolma.utility.csv import CSV
from jaolma.gis.wfs import Feature, Collection
from jaolma.gis.wmts import WMTS
from jaolma.plotting.maps import Map
from jaolma.utility.utility import prints, printe

import sys
import os

if len(sys.argv) > 1:
    file_paths = sys.argv[1:]
    
else:
    path = os.path.join(os.getcwd(), 'files/area_data/')

    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith('.csv')]

    file_paths = None
    while file_paths == None:
        print('\n'.join([f'{i + 1}: {dir}' for i, dir in enumerate(files)]))
        i = input('Please select an option or enter the full path of a .csv file: ')

        if i.isnumeric():
            i = int(i) - 1
            if 0 > i or i >= len(files):
                printe('Invalid index.')
                continue

            file_name = files[i]
            file_paths = [os.path.join(path, file_name)]

        else:
            prints(f'Using path \'{i}\'.')
            file_paths = [i]

for file_path in file_paths:
    csv = CSV(file_path, delimiter=',')
    content = csv.load()

    file_name = os.path.split(file_path)[-1][:-4]
    area, source = file_name.split('_')

    center = Properties.areas[area]

    prints(f'Plotting map for file \'{file_name}\'.')

    features = []
    for row in content:
        geometry = [[float(v) for v in s.split(',')] for s in row['geometry'][1:-1].split(';')[1:]]

        if len(geometry) == 1:
            geometry = geometry[0]
        else:
            pass
            geometry = [[pos[0] for pos in geometry], [pos[1] for pos in geometry]] 

        tag = row['geometry'][1:-1].split(';')[0]

        del row['geometry']

        features.append(Feature(geometry, srs=Properties.default_srs, tag=tag, attributes=row))

    if len(features) == 0:
        input('No features in file.')
        exit()

    features = Collection(tag=source.capitalize(), type=features[0].tag, features=features, srs=features[0].default_srs)

    wmts = WMTS(use_login=True, url='https://services.datafordeler.dk/GeoDanmarkOrto/orto_foraar_wmts/1.0.0/WMTS?', 
        username='VCSWRCSUKZ',
        password='hrN9aTirUg5c!np',
        layer='orto_foraar_wmts',
        tile_matrix_set='KortforsyningTilingDK')

    tile_matrix = 15
    bounding_margin = 10

    dpi = 300
    figsize = (16, 16)

    annotations = [feature['#'] for feature in features]

    center.to_srs('EPSG:25832')

    map = Map(center, wmts, figname=file_name, tile_matrix=tile_matrix, draw_center=True, figsize=figsize, dpi=dpi)
    map.add_feature(features, annotations)
    map.show(show=(len(file_paths) == 1))

input('Press enter to close.')