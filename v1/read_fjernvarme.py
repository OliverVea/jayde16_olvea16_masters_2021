from jaolma.utility.csv import *
from jaolma.properties import Properties
from math import sqrt
import json, os

radius = 100

for area in Properties.areas:

    center = Properties.areas[area].as_srs(srs='EPSG:25832').points['EPSG:25832']

    with open("input/FjernvarmeFyn/Casings.json", "r") as f:
        input_data = json.load(f)
    all_features = input_data['features']

    features = []
    for ft in all_features:
        if sqrt((ft['geometry']['x'] - center[0])**2 + (ft['geometry']['y'] - center[1])**2) < radius:
            features.append(ft)


    #input_data = input_csv.load(filter=filter)

    output_data = []

    for i, row in enumerate(features):
        output_data.append({})
        output_data[i]['#'] = i
        output_data[i]['id'] = row['attributes']['GlobalID']
        output_data[i]['name'] = 'heating_cover'
        output_data[i]['description'] = 'Cover from Fjernvarme Fyn'
        output_data[i]['geometry'] = f'"Point;{row["geometry"]["x"]},{row["geometry"]["y"]},{row["geometry"]["z"]}"'
        output_data[i]['diameter_cm'] = row['attributes']['CAPCODE']
        output_data[i]['shape'] = row['attributes']['CASINGFORM']
        output_data[i]['n_caps'] = row['attributes']['NUMCAPS']
        output_data[i]['rotation'] = row['attributes']['ROTATION']
        output_data[i]['owner'] = row['attributes']['OWNER']
        output_data[i]['last_update'] = row['attributes']['EDITED']

    if len(output_data) > 0:
        types = [type(typ).__name__ for typ in output_data[0].values()]
        CSV.create_file('files/area_data/' + area + '_fjernvarme.csv', delimiter=',', header=output_data[0].keys(), content=output_data, types=types)