import pandas as pd

filename = 'gt_sdu_25832.csv'

input_file = pd.read_csv(filename)[::-1]

prev_ids = []
dataframe = pd.DataFrame(columns=input_file.columns)

for i, row in input_file.iterrows():

    id = row['ID']

    if id not in prev_ids:
        prev_ids.append(id)
        
        dataframe = dataframe.append(row.copy(deep=True))
        
dataframe.to_csv('gt_sdu.csv')