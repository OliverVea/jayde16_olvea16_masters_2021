import pandas as pd

from pyproj import Transformer

#areas = ['downtown', 'harbor', 'park', 'sdu', 'suburb']

#points = [[55.39502938, 10.38263004], [55.39427098, 10.38458007], [55.39414598, 10.38476681], [55.39409501, 10.38503692]]
#transformed_points = []

transformer = Transformer.from_crs('EPSG:4326', 'EPSG:25832')

#for point in points:
#    transformed_points.append(transformer.transform(point[0], point[1]))

#print(transformed_points)

#for area in areas:

input_file = pd.read_csv(f'data_labelled.csv')
for idx in range(len(input_file.index)):
    lat = input_file['lat'].values[idx]
    lon = input_file['lon'].values[idx]

    [x, y] = transformer.transform(lat, lon)

    input_file['lat'].values[idx] = x
    input_file['lon'].values[idx] = y

#input_file.columns.values[3] = 'x'
#input_file.columns.values[5] = 'y'
input_file.to_csv(f'data_labelled_25832.csv')