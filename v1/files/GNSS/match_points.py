import pandas as pd
from math import sqrt
from pyproj import Transformer

input = pd.read_csv('GNSS_sdu - Copy.csv')

current_features = [row[1] for row in input.iterrows() if int(row[1]['ID']) < 310]

new_features = [row[1] for row in input.iterrows() if int(row[1]['ID']) >= 310]

transformer = Transformer.from_crs("EPSG:4326", "EPSG:25832")

for ft in current_features:
    ft['epsg:25832'] = transformer.transform(ft['lat'], ft['lon'])
    
for ft in new_features:
    ft['epsg:25832'] = transformer.transform(ft['lat'], ft['lon'])

id_dict = {}
for new_row in new_features:
    for curr_row in current_features:
        distance = sqrt((new_row['epsg:25832'][0]-curr_row['epsg:25832'][0])**2 + (new_row['epsg:25832'][1]-curr_row['epsg:25832'][1])**2)
        if distance < 0.3:
            id_dict[new_row['ID']] = (curr_row['ID'], distance)
            #print('distance:', distance, 'features:', curr_row['ID'], new_row['ID'])
        #if new_row[]

for row_id in input.ID:
    if row_id in id_dict:
        input['ID'] = input['ID'].replace([row_id], id_dict[row_id][0])

input.to_csv('GNSS_sdu_with_second.csv')

'''
for new_row in new_features:
    for curr_row in current_features:
        distance = sqrt((new_row['lat']-curr_row['lat'])**2 + (new_row['lon']-curr_row['lon'])**2)
        if distance < 0.0:
            print(distance)
        #if new_row[]
'''