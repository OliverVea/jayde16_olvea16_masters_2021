from jaolma.properties import Properties
from jaolma.utility.csv import CSV
from jaolma.gis.wfs import Feature, Collection
from jaolma.gis.wmts import WMTS
from jaolma.plotting.maps import Map
from jaolma.utility.utility import prints, printe, transpose

import sys
import os

import matplotlib.pyplot as plt

import pandas as pd

def get_next_id(path: str = 'files/validation'):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith('.csv')]

    if len(files) == 0:
        return 1

    ids = [int(f.split('_')[0]) for f in files]
    return max(ids) + 1

if len(sys.argv) > 1:
    file_paths = sys.argv[1:]
    
else:
    path = os.path.join(os.getcwd(), 'files/areas/')

    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith('.csv')]

    file_paths = []
    additional_input = False

    while file_paths == [] or additional_input:
        print('\n'.join([f'{i + 1}: {dir}' for i, dir in enumerate(files)]))
        i = input('Please select an option or enter the full path of a .csv file: ')

        if i.isnumeric():
            i = int(i) - 1
            if 0 > i or i >= len(files):
                printe('Invalid index.')
                continue

            file_name = files[i]
            file_paths.append(os.path.join(path, file_name))

        else:
            prints(f'Using path \'{i}\'.')
            file_paths.append(i)

            
        i = input('Would you like to add another file? (y/n): ')
        additional_input = (i == 'y')


for area, center in zip(Properties.areas.keys(), Properties.areas.values()):
    files = [pd.read_csv(file_path) for file_path in file_paths if os.path.split(file_path)[-1][:-4].split('_')[1] == area]

    if len(files) == 0:
        continue

    validation_id = get_next_id()

    dataframe = pd.concat(files, ignore_index=True)
    dataframe.rename(columns={'Unnamed: 0': 'old_n'})
    dataframe.to_csv(f'files/validation/{validation_id}_{area}_data.csv')

    prints(f'Plotting map for area \'{area}\'.')

    features = {}
    for n, row in dataframe.iterrows():
        row = dict(row)

        row['n'] = n

        geometry = row['geometry'].split(';')[1].split(',')
        geometry = [g[1:-1] for g in geometry]
        geometry = transpose([[float(v) for v in g.split(',')] for g in geometry])

        if len(geometry) == 1:
            geometry = geometry[0]
        else:
            geometry = [[pos[0] for pos in geometry], [pos[1] for pos in geometry]] 

        tag = row['geometry'].split(';')[0]

        del row['geometry']

        feature = Feature(geometry, srs=Properties.default_srs, tag=tag, attributes=row)
        features.setdefault(row['typename'], []).append(feature)

    if len(features) == 0:
        prints('No features in file.')
        continue

    wmts = WMTS(use_login=True, url='https://services.datafordeler.dk/GeoDanmarkOrto/orto_foraar_wmts/1.0.0/WMTS?', 
        username='VCSWRCSUKZ',
        password='hrN9aTirUg5c!np',
        layer='orto_foraar_wmts',
        tile_matrix_set='KortforsyningTilingDK')

    tile_matrix = 15
    bounding_margin = 10

    dpi = 300
    figsize = (16, 16)

    center.to_srs(Properties.default_srs)

    map = Map(center, wmts, figname=f'files/validation/{validation_id}_{area}_map', tile_matrix=tile_matrix, draw_center=True, figsize=figsize, dpi=dpi)
    map.add_circle(center, Properties.radius)

    for typename, feature_list in zip(features.keys(), features.values()):
        collection = Collection(tag=str(validation_id), type=feature_list[0].tag, features=feature_list, srs=feature_list[0].default_srs)

        annotations = [feature['n'] for feature in feature_list]
        label = Properties.feature_properties[typename]['label']
        color = Properties.feature_properties[typename]['color']

        map.add_feature(collection, annotations=annotations, label=label, color=color)

    map.show()
    plt.close()

input('Press enter to close.')