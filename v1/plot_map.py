from jaolma.properties import Properties
from jaolma.utility.csv import CSV
from jaolma.gis.wfs import Feature

import sys
import os

file_path = r'D:\WindowsFolders\Documents\GitHub\jayde16_olvea16_masters_2021\v1\files\_Node_Cover_wHeader.csv'
if file_path == None:
    if len(sys.argv) > 1:
        file_path = sys.argv[1]

    else:
        path = os.path.join(os.getcwd(), 'files/area_data/')

        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith('.csv')]

        file_path = None
        while file_path == None:
            print('\n'.join([f'{i + 1}: {dir}' for i, dir in enumerate(files)]))
            i = input('Please select an option or enter the full path of a .csv file: ')

            if i.isnumeric():
                i = int(i) - 1
                if 0 > i or i >= len(files):
                    print('Invalid index.')
                    continue

                file_name = files[i]
                file_path = os.path.join(file_name, dir)

            else:
                print(f'Using path \'{i}\'.')
                file_path = i

csv = CSV(file_path, delimiter=',')
content = csv.load()

file_name = os.path.split(file_path)[-1][:-3]
area, source = file_name.split('_')

center = Properties.areas[area]

features = []
for row in content:
    geometry = [[float(v) for v in s.split(',')] for s in row['geometry'][1:-1].split(';')[1:]]
    tag = row['geometry'][1:-1].split(';')[0]

    del row['geometry']

    features.append(Feature(geometry, srs=Properties.default_srs, tag=tag, attributes=row))

