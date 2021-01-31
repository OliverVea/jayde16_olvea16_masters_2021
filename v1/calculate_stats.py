import os
import pandas as pd

from jaolma.properties import Properties
from jaolma.utility.utility import transpose
from jaolma.gis.wfs import Feature


def get_area_data(area: str):    
    path = 'files/areas'
    files = [file for file in os.listdir(path) if os.path.split(file)[-1][:-4].split('_')[1] == area and os.path.split(file)[-1][:-4].split('_')[2] != '0']
    files = {file.split('_')[0]: pd.read_csv(f'{path}/{file}') for file in files}

    gt_features = ['Tree', 'Light Fixture', 'Downspout Grille', 
                   'Manhole Cover', 'Fuse Box', 'Building Corner',
                   'Bench', 'Trash Can', 'Tree Stump', 'Chimney', 
                   'Rock', 'Statue', 'Misc', 'Greenery']

    used_features = {'groundtruth': gt_features,
                     'fjernvarme': ['heating_cover'], 
                     'energifyn': ['TL740800', 'TL740798'],
                     'kortopslag': ['L418883_421469', 'TL965167', 'TL695099'],
                     'samaqua': ['water_node'],
                     'geodanmark': ['Broenddaeksel','Mast','Trae','Nedloebsrist','Skorsten']}  

    features_translation = {'heating_cover': 'Manhole Cover', 'TL740800': 'Light Fixture', 'TL740798': 'Fuse Box', 
                            'L418883_421469': 'Downspout Grille', 'TL965167': 'Tree', 'TL695099': 'Bench',
                            'water_node': 'Manhole Cover', 'Broenddaeksel': 'Manhole Cover',  'Mast': 'Light Fixture',  
                            'Trae': 'Tree', 'Nedloebsrist': 'Downspout Grille', 'Skorsten': 'Chimney'}

    #Smid alt data for området ind i en dict.
    all_data = {}
    for source, data in zip(files.keys(), files.values()):
        all_data[source] = []
        for n, row in data.iterrows():
            row_dict = dict(row)
    
            all_data[source].append(row_dict)

    #Count amount of all features - vi skal have sorteret dem fra i downtown, har lavet en fil med dem der skal excludes i groundtruth mappen.
    #Her skal vi have tilføjet alt der skal ekskluderes og så tjekke for det her tænker jeg.
    amount_features = {}
    for source in used_features.keys():
        for typename in used_features[source]:
            amount_features[typename] = 0
            for ft in all_data[source]:
                if ft['typename'] == typename:
                    amount_features[typename] += 1


    #Calculate True and False positive
    del(used_features['groundtruth'])
    stats = {}
    for source in used_features.keys():
        for typename in used_features[source]:
            stats[typename] = {'True Positive': 0, 'False Positive': 0, 'False Negative': 0}
            for ft in all_data[source]:
                if ft['typename'] == typename:
                    ft_exists = False
                    for true_ft in all_data['groundtruth']:
                        if ft['id'] == true_ft[source]:
                            ft_exists = True
                            break
                    if ft_exists:
                        stats[typename]['True Positive'] += 1
                    else:
                        stats[typename]['False Positive'] += 1

    #I know, jeg kan heller ikke lide at neste så mange loops... Men det virker ish...

    return stats

def area_precision(area):
    pass

def source_precision(source):
    pass

def area_recall(area):
    pass

def source_precision(source):
    pass

areas = ['downtown', 'park', 'suburbs', 'harbor', 'sdu']
for area in areas:
    print(area, get_area_data('downtown'))