import pandas as pd

from pyproj import Transformer

filename = 'gt_sdu_25832.csv'

transformer = Transformer.from_crs('EPSG:4326', 'EPSG:25832')

input_file = pd.read_csv(filename)

prev_ids = []
dataframe = pd.DataFrame(columns=input_file.columns)

for row in input_file.iterrows():

    id = row[1]['ID']

    if id not in prev_ids:
        prev_ids.append(id)
        
        dataframe.append(row[1])
        
        dummy = 0


#input_file.to_csv(f'gt_{area}_25832.csv')