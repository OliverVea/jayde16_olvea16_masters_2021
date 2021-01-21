import pandas as pd

from pyproj import Transformer

areas = ['downtown', 'harbor', 'park', 'sdu', 'suburb']

transformer = Transformer.from_crs('EPSG:4326', 'EPSG:25832')

for area in areas:
    input_file = pd.read_csv(f'gt_{area}.csv')
    for idx in range(len(input_file.index)):
        lat = input_file['lat'].values[idx]
        lon = input_file['lon'].values[idx]

        [x, y] = transformer.transform(lat, lon)

        input_file['lat'].values[idx] = x
        input_file['lon'].values[idx] = y

    input_file.columns.values[3] = 'x'
    input_file.columns.values[5] = 'y'
    input_file.to_csv(f'gt_{area}_25832.csv')