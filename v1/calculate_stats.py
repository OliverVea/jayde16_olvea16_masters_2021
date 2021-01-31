import os
import pandas as pd

from jaolma.properties import Properties
from jaolma.utility.utility import transpose
from jaolma.gis.wfs import Feature

def get_area_data(area: str):    
    path = 'files/areas'
    files = [file for file in os.listdir(path) if os.path.split(file)[-1][:-4].split('_')[1] == area and os.path.split(file)[-1][:-4].split('_')[2] != '0']
    files = {file.split('_')[0]: pd.read_csv(f'{path}/{file}') for file in files}
    
    result = {}
    for source, data in zip(files.keys(), files.values()):
        features = {}
        for n, row in data.iterrows():
            row = dict(row)

            row['n'] = n

            geometry = row['geometry'].split(';')[1].split(',')
            geometry = [g[1:-1] for g in geometry]
            geometry = transpose([[float(v) for v in g.split(',')] for g in geometry])

            if len(geometry) == 1:
                geometry = geometry[0]
            else:
                geometry = [[pos[0] for pos in geometry], [pos[1] for pos in geometry]] 

            tag = row['geometry'].split(';')[0]

            del row['geometry']

            feature = Feature(geometry, srs=Properties.default_srs, tag=tag, attributes=row)
            features.setdefault(row['typename'], []).append(feature)
        result[source] = features

    return result


def calculate_stats(area: str):    
    #path = 'files/areas'
    #files = [file for file in os.listdir(path) if os.path.split(file)[-1][:-4].split('_')[1] == area and os.path.split(file)[-1][:-4].split('_')[2] != '0']
    #files = {file.split('_')[0]: pd.read_csv(f'{path}/{file}') for file in files}

    data = get_area_data(area)
    ground_truth = data['groundtruth']
    del data['groundtruth']

    # This is kind of used as a check for which foreign feature type should appear as which ground truth feature type.
    # Needs heavy expansion.
    features_translation = {'heating_cover': 'Manhole Cover', 'TL740800': 'Light Fixture', 'TL740798': 'Fuse Box', 
                            'L418883_421469': 'Downspout Grille', 'TL965167': 'Tree', 'TL695099': 'Bench',
                            'water_node': 'Manhole Cover', 'Broenddaeksel': 'Manhole Cover',  'Mast': 'Light Fixture',  
                            'Trae': 'Tree', 'Nedloebsrist': 'Downspout Grille', 'Skorsten': 'Chimney'}

    false_negatives = {source: {typename: 0 for typename in data[source]} for source in data}

    # THIS LOOP IS RESPONSIBLE FOR MAPPING!
    mapped_features = {}
    for gt_type in ground_truth:
        gt_features = ground_truth[gt_type]

        for gt_ft in gt_features:
            for source in data:
                if pd.notna(gt_ft[source]):
                    # True positive mapping
                    mapped_features.setdefault(source, []).append(gt_ft[source])
                else:
                    # Check for false negatives
                    for typename in features_translation:
                        if gt_type == features_translation[typename] and typename in data[source]:
                            # Count false negatives
                            false_negatives[source][typename] += 1

    # Apply mappings to foreign features
    for source in data:
        for typename in data[source]:
            features = data[source][typename]
            for i, ft in enumerate(features):
                data[source][typename][i]['mapped'] = (source in mapped_features and ft['id'] in mapped_features[source])

    # Count true and false positives
    true_positives = {source: {typename: sum(1 for ft in data[source][typename] if ft['mapped']) for typename in data[source]} for source in data}
    false_positives = {source: {typename: sum(1 for ft in data[source][typename] if not ft['mapped']) for typename in data[source]} for source in data}
    n_features = {source: {typename: sum(1 for ft in data[source][typename]) for typename in data[source]} for source in data}
    
    def calculation(tp, fp):
        if (tp + fp) == 0:
            return None
        return tp / (tp + fp)

    precision = {source: {typename: calculation(true_positives[source][typename], false_positives[source][typename]) for typename in data[source]} for source in data}
    recall = {source: {typename: calculation(true_positives[source][typename], false_negatives[source][typename]) for typename in data[source]} for source in data}

    print(f'Analysis for {area}:')
    for source in data:
        print(f'Source - {source}.')
        for typename in data[source]:
            print(f'{Properties.feature_properties[typename]["label"]}:')
            print(f'N: {n_features[source][typename]}')
            print(f'TP: {true_positives[source][typename]}')
            print(f'FP: {false_positives[source][typename]}')
            print(f'FN: {false_negatives[source][typename]}')
            print(f'Precision: {precision[source][typename]*100:.1f}%')

            if recall[source][typename] != None:
                print(f'Recall: {recall[source][typename]*100:.1f}%')
            
            print('')
        print('\n---\n')

    pass
    # # Ground truth feature types
    # gt_features = ['Tree', 'Light Fixture', 'Downspout Grille', 
    #                'Manhole Cover', 'Fuse Box', 'Building Corner',
    #                'Bench', 'Trash Can', 'Tree Stump', 'Chimney', 
    #                'Rock', 'Statue', 'Misc', 'Greenery']
    # gt_features = list(ground_truth.keys())

    # # De features vi bruger (hardcoded for some reason :shrug:)
    # used_features = {'groundtruth': gt_features,
    #                  'fjernvarme': ['heating_cover'], 
    #                  'energifyn': ['TL740800', 'TL740798'],
    #                  'kortopslag': ['L418883_421469', 'TL965167', 'TL695099'],
    #                  'samaqua': ['water_node'],
    #                  'geodanmark': ['Broenddaeksel','Mast','Trae','Nedloebsrist','Skorsten']}  


    # # #Smid alt data for området ind i en dict.
    # # all_data = {}
    # # for source, data in zip(files.keys(), files.values()):
    # #     all_data[source] = []
    # #     for n, row in data.iterrows():
    # #         row_dict = dict(row)
    
    # #         all_data[source].append(row_dict)

    # #Count amount of all features - vi skal have sorteret dem fra i downtown, har lavet en fil med dem der skal excludes i groundtruth mappen.
    # #Her skal vi have tilføjet alt der skal ekskluderes og så tjekke for det her tænker jeg.
    # amount_features = {}
    # for source in used_features.keys():
    #     for typename in used_features[source]:
    #         amount_features[typename] = 0
    #         for ft in all_data[source]:
    #             if ft['typename'] == typename:
    #                 amount_features[typename] += 1
    
    # amount_features = {typename: sum([1 for ft in all_data[source] if ft['typename'] == typename]) for source in used_features for typename in used_features[source]}


    # #Calculate True and False positive
    # del(used_features['groundtruth'])
    # stats = {}
    # for source in used_features.keys():
    #     for typename in used_features[source]:
    #         stats[typename] = {'True Positive': 0, 'False Positive': 0, 'False Negative': 0}
    #         for ft in all_data[source]:
    #             if ft['typename'] == typename:
    #                 ft_exists = False
    #                 for true_ft in all_data['groundtruth']:
    #                     if ft['id'] == true_ft[source]:
    #                         ft_exists = True
    #                         break
    #                 if ft_exists:
    #                     stats[typename]['True Positive'] += 1
    #                 else:
    #                     stats[typename]['False Positive'] += 1

    # #I know, jeg kan heller ikke lide at neste så mange loops... Men det virker ish...

    # return stats

def area_precision(area):
    pass

def source_precision(source):
    pass

def area_recall(area):
    pass

def source_precision(source):
    pass

areas = ['downtown', 'park', 'suburb', 'harbor', 'sdu']
areas = ['suburb']
for area in areas:
    #print(area, calculate_stats(area))
    calculate_stats(area)
