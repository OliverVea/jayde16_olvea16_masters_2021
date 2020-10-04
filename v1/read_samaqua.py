from jaolma.utility.csv import *
from jaolma.properties import Properties
from math import sqrt

radius = 100

for area in Properties.areas:

    center = area.as_srs(srs='EPSG:25832').points['EPSG:25832']

    def filter(row):
        if row['X_Node'] != None:
            if sqrt((row['X_Node'] - center[0])**2 + (row['Y_Node'] - center[1])**2) < radius:
                return True

        if row['X_Cover'] != None:
            return sqrt((row['X_Cover'] - center[0])**2 + (row['Y_Cover'] - center[1])**2) < radius

        return False
        

    input_csv = CSV('input/Node_Cover_wHeader.csv', delimiter=',', type_row = True)
    input_data = input_csv.read(filter=filter)

    output_data = [{}]*len(input_data)

    cover_number = len(input_data)
    for i, row in enumerate(input_data):
        if row['X_Cover'] == None:
            output_data[i]['#'] = i
            output_data[i]['ID'] = row['FeatureGUID'] + '_node'
            output_data[i]['Description'] = 'Water node'
            output_data[i]['Geometry'] = f'{row["X_Node"]}, {row["Y_Node"]}'
        else:
            output_data.append({})
            output_data[cover_number]['#'] = cover_number
            output_data[cover_number]['ID'] = row['FeatureGUID'] + '_cover'
            output_data[cover_number]['Description'] = 'Water cover'
            output_data[cover_number]['Geometry'] = f'{row["X_Cover"]}, {row["Y_Cover"]}'
            cover_number += 1



    #out = CSV('input/_Node_Cover_wHeader.csv', delimiter=',', type_row = True)
    #out.write(a)
    dummy = 0
    pass