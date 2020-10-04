from jaolma.utility.csv import *
from jaolma.properties import Properties
from math import sqrt

radius = 100

for area in Properties.areas:

    center = Properties.areas[area].as_srs(srs='EPSG:25832').points['EPSG:25832']

    def filter(row):
        if row['X_Node'] != None:
            return sqrt((row['X_Node'] - center[0])**2 + (row['Y_Node'] - center[1])**2) < radius
        return False

    input_csv = CSV('input/Samaqua/Node_Cover_wHeader.csv', delimiter=';')
    input_data = input_csv.load(filter=filter)

    output_data = [{} for _ in input_data]

    for i, row in enumerate(input_data):
        output_data[i]['#'] = i
        output_data[i]['id'] = row['FeatureGUID'] + '_node'
        output_data[i]['description'] = 'Water node'
        output_data[i]['geometry'] = f'"Point;{row["X_Node"]},{row["Y_Node"]}"'

    if len(output_data) > 0:
        types = [type(typ).__name__ for typ in output_data[0].values()]
        CSV.create_file('files/area_data/' + area + '_samaqua.csv', delimiter=',', header=output_data[0].keys(), content=output_data, types=types)