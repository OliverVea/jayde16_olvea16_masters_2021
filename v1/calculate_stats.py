import os
import pandas as pd

from jaolma.properties import Properties
from jaolma.utility.utility import transpose
from jaolma.gis.wfs import Feature

from numpy import mean as avg

def flatten(dictionary):
    return [b for a in dictionary for b in dictionary[a]]

class GISData:
    all_sources = list(set(Properties.feature_properties[typename]['origin'] for typename in Properties.feature_properties))
    all_typenames = {source: {typename for typename in Properties.feature_properties if Properties.feature_properties[typename]['origin'] == source} for source in all_sources}

    class Stats:
        # Same equation used to calculate precision and recall.
        def _calc(self, a: float, b: float):
            if (a + b) == 0:
                return None
            return a / (a + b)

        def __init__(self, source, typename, gt_ids: list, source_ids: list,
                amount: int = None, 
                true_positives: int = None, 
                false_positives: int = None, 
                false_negatives: int = None, 
                accuracies: list = [],
                accessibilities: list = [], 
                visibilities: list = []):

            self.source = source 
            self.typename = typename
            self.gt_ids = gt_ids
            self.source_ids = source_ids
            self.amount = amount

            self.true_positives = true_positives
            self.false_positives =false_positives
            self.false_negatives = false_negatives

            self.accuracies = accuracies

            self.accessibilities = accessibilities
            self.visibilities = visibilities

        def get_accessibility(self):
            return avg(self.accessibilities)

        def get_visibility(self):
            return avg(self.visibilities)

        def get_precision(self):
            return self._calc(self.true_positives, self.false_positives)

        def get_recall(self):
            return self._calc(self.true_positives, self.false_negatives)

        def get_f1(self):
            return 2 / (1 / self.get_recall() + 1 / self.get_precision())

        def get_accuracy(self):
            return avg(self.accuracies)

    # TODO: Måske en klasse der håndterer n:1, 1:n og n:n matches?
    # 'source' -> 'service' bedre navn. ground truth features vs. service features.
    class Match:
        def __init__(self, gt_ids, service_ids):
            pass

    def _get_data(self, features_to_exclude: list = []):
        # TODO: Exclude features
        path = 'files/areas'
        files = [file for file in os.listdir(path) if os.path.split(file)[-1][:-4].split('_')[1] == self.area and os.path.split(file)[-1][:-4].split('_')[2] != '0']
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

    def _get_validation_results(self, source, features):
        path = f'files/validation/new_{self.area}.csv'
        data = pd.read_csv(path)

        feature_ids = [ft['id'] for ft in features]

        acc = [row['Accessibility'] for n, row in data.iterrows() if row['Feature ID'] in feature_ids]
        ovis = [row['Obstructed Visibility'] for n, row in data.iterrows() if row['Feature ID'] in feature_ids]
        vis = [100 * (a/100 + (1 - a/100) * v/100) for a, v in zip(acc, ovis)]

        return acc, vis

    # This function returns whether or not a ground truth feature should qualify as some source feature type.
    def _should_qualify(self, feature, typename):
        # TODO: add radius

        translation = {'heating_cover': 'Manhole Cover', 'TL740800': 'Fuse Box', 'TL740798': 'Light Fixture', 
            'L418883_421469': 'Downspout Grille', 'TL965167': 'Tree', 'TL695099': 'Bench',
            'water_node': 'Manhole Cover', 'Broenddaeksel': 'Manhole Cover',  'Mast': 'Light Fixture',  
            'Trae': 'Tree', 'Nedloebsrist': 'Downspout Grille', 'Skorsten': 'Chimney'}

        for _typename in Properties.feature_properties:
            if Properties.feature_properties[_typename]['origin'] != 'groundtruth' and not _typename in translation:
                translation[_typename] = None

        return feature['typename'] == translation[typename]

    # KODEN VIRKER KUN MED 1-1 MATCHES!! FIX!!
    # KODEN VIRKER KUN MED 1-1 MATCHES!! FIX!!
    # KODEN VIRKER KUN MED 1-1 MATCHES!! FIX!!
    # KODEN VIRKER KUN MED 1-1 MATCHES!! FIX!!
    # KODEN VIRKER KUN MED 1-1 MATCHES!! FIX!!
    # KODEN VIRKER KUN MED 1-1 MATCHES!! FIX!!
    # KODEN VIRKER KUN MED 1-1 MATCHES!! FIX!!
    def _get_stats(self):
        stats = {source: {typename: None for typename in self.all_typenames[source]} for source in self.all_sources} 
        
        for source in self.data:
            matched_features = [ft for typename in self.ground_truth for ft in self.ground_truth[typename] if not pd.isna(ft[source])]
            matches = [ft[source] for ft in matched_features]
            accessibilities, visibilities = self._get_validation_results(source, matched_features)

            for typename in self.data[source]:
                ids = [ft['id'] for ft in self.data[source][typename]]

                # Count features
                N = len(self.data[source][typename])

                # Count true positives
                tp = sum(1 for ft in self.data[source][typename] if ft['id'] in matches)

                # Count false positives
                fp = sum(1 for ft in self.data[source][typename] if not ft['id'] in matches)

                # Count false negatives
                N_gt = sum(1 for ft in flatten(self.ground_truth) if self._should_qualify(ft, typename))
                fn = N_gt - tp

                # Get accessibility and visibility
                acc = [acc for ft, acc in zip(matched_features, accessibilities) if ft[source] in ids]
                vis = [vis for ft, vis in zip(matched_features, visibilities) if ft[source] in ids]

                # Get accuracy
                err = []
                
                stats[source][typename] = self.Stats(source, typename, gt_ids=[ft['id'] for ft in matched_features], source_ids=[ft[source] for ft in matched_features], amount=N, true_positives=tp, false_positives=fp, false_negatives=fn, accessibilities=acc, visibilities=vis, accuracies=err)
                print()


        return stats

    def __init__(self, area: str):
        self.area = area
        self.data = self._get_data()
        self.ground_truth = self.data['groundtruth']
        del self.data['groundtruth']

        self.stats = self._get_stats()

        return

d = GISData('harbor')

def calculate_stats(area: str):    
    data = get_area_data(area)
    ground_truth = data['groundtruth']
    del data['groundtruth']

    # This is kind of used as a check for which foreign feature type should appear as which ground truth feature type.
    # Needs heavy expansion.
    # features_translation = {'heating_cover': 'Manhole Cover', 'TL740800': 'Fuse Box', 'TL740798': 'Light Fixture', 
    #                         'L418883_421469': 'Downspout Grille', 'TL965167': 'Tree', 'TL695099': 'Bench',
    #                         'water_node': 'Manhole Cover', 'Broenddaeksel': 'Manhole Cover',  'Mast': 'Light Fixture',  
    #                         'Trae': 'Tree', 'Nedloebsrist': 'Downspout Grille', 'Skorsten': 'Chimney'}

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
    n_features = {source: {typename: sum(1 for ft in data[source][typename]) for typename in data[source]} for source in data}
    true_positives = {source: {typename: sum(1 for ft in data[source][typename] if ft['mapped']) for typename in data[source]} for source in data}
    false_positives = {source: {typename: sum(1 for ft in data[source][typename] if not ft['mapped']) for typename in data[source]} for source in data}
    
    def calc(a, b):
        if (a + b) == 0:
            return None
        return a / (a + b)

    precision = {source: {typename: calc(true_positives[source][typename], false_positives[source][typename]) for typename in data[source]} for source in data}
    recall = {source: {typename: calc(true_positives[source][typename], false_negatives[source][typename]) for typename in data[source]} for source in data}

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
#areas = ['harbor']
for area in areas:
    #print(area, calculate_stats(area))
    calculate_stats(area)
