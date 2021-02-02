import os
import pandas as pd

from jaolma.properties import Properties
from jaolma.utility.utility import transpose
from jaolma.gis.wfs import Feature

from numpy import mean as avg
from numpy import sqrt

def flatten(dictionary):
    return [b for a in dictionary for b in dictionary[a]]

class GISData:
    all_sources = list(set(Properties.feature_properties[typename]['origin'] for typename in Properties.feature_properties if Properties.feature_properties[typename]['origin'] != 'groundtruth'))
    all_typenames = {source: {typename for typename in Properties.feature_properties if Properties.feature_properties[typename]['origin'] == source} for source in all_sources}

    class Stats:
        # Same equation used to calculate precision and recall.
        def _calc(self, a: float, b: float):
            if (a + b) == 0:
                return None
            return a / (a + b)

        def __init__(self, source, typename, gt_ids: list, service_ids: list,
                amount: int = None, 
                true_positives_gt: list = None,
                true_positives: list = None, 
                false_positives: list = None, 
                false_negatives: list = None, 
                accuracies: list = [],
                accessibilities: list = [], 
                visibilities: list = [],
                matches: list = []):

            self.source = source 
            self.typename = typename
            self.gt_ids = gt_ids
            self.service_ids = service_ids
            self.amount = amount

            self.true_positives = true_positives
            self.true_positives_gt = true_positives_gt
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
            return self._calc(len(self.true_positives), len(self.false_positives))

        def get_recall(self):
            return self._calc(len(self.true_positives), len(self.false_negatives))

        def get_f1(self):
            return 2 / (1 / self.get_recall() + 1 / self.get_precision())

        def get_accuracy(self):
            return avg(self.accuracies)

    class Match:
        def __init__(self, gt_ids, service_ids):
            self.gt_ids = gt_ids
            self.service_ids = service_ids
        
        def is_matched(self, gt_id: str = None, service_id: str = None) -> bool:
            if gt_id == None and service_id == None:
                raise Exception('Please specify an of either type.')
        
            if gt_id != None and service_id != None:
                raise Exception('Please only specify one id.')

            if gt_id != None:
                return gt_id in self.gt_ids
            return service_id in self.service_ids

    def _get_data(self, features_to_exclude: list = [], use_exclude_property: bool = False):
        # TODO: Exclude features
        path = 'files/areas'
        files = [file for file in os.listdir(path) if os.path.split(file)[-1][:-4].split('_')[1] == self.area and os.path.split(file)[-1][:-4].split('_')[2] != '0']
        files = {file.split('_')[0]: pd.read_csv(f'{path}/{file}', dtype=str) for file in files}
        
        result = {}
        for source, data in zip(files.keys(), files.values()):
            features = {}
            for n, row in data.iterrows():
                row = dict(row)

                typename = row['typename']
                if use_exclude_property and Properties.feature_properties[typename]['exclude']:
                    continue

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

    def _get_validation_results(self, source, matches):
        path = f'files/validation/new_{self.area}.csv'
        data = pd.read_csv(path)

        # TODO: Might cause problems.
        feature_ids = [match.gt_ids[0] for match in matches]

        acc = [row['Accessibility'] for n, row in data.iterrows() if str(row['Feature ID']) in feature_ids]
        
        ovis = [row['Obstructed Visibility'] for n, row in data.iterrows() if str(row['Feature ID']) in feature_ids]
        vis = [100 * (a/100 + (1 - a/100) * v/100) for a, v in zip(acc, ovis)]

        return acc, vis

    def _get_matches(self, source):
        matches = []
        for ft in flatten(self.ground_truth):
            if not pd.isna(ft[source]):
                service_ids = [t.rstrip() for t in ft[source].split(',')]
                match = self.Match(gt_ids=[ft['id']], service_ids=service_ids)
                matches.append(match)

        return matches

    # This function returns whether or not a ground truth feature should qualify as some service feature type.
    def _should_qualify(self, feature, typename):
        # TODO: add circle radius

        translation = {'heating_cover': ['Manhole Cover'], 'TL740800': ['Fuse Box'], 'TL740798': ['Light Fixture'], 
            'L418883_421469': ['Tree'], 'TL965167': ['Downspout Grille', 'Manhole Cover'], 'L167365_421559': ['Bench', 'Trash Can', 'Statue', 'Misc', 'Rock'],
            'water_node': ['Manhole Cover'], 'Broenddaeksel': ['Manhole Cover'],  'Mast': ['Light Fixture'],  
            'Trae': ['Tree'], 'Nedloebsrist': ['Downspout Grille'], 'Skorsten': ['Chimney']}

        for _typename in Properties.feature_properties:
            if Properties.feature_properties[_typename]['origin'] != 'groundtruth' and not _typename in translation:
                translation[_typename] = []

        if not feature['typename'] in translation[typename]:
            return False

        source = Properties.feature_properties[typename]

        # Manhole covers: 
        # Kun brug Large (geodanmark, samaqua, kortopslag, fjernvarme) og Large Square (samaqua, geodanmark)
        if feature['typename'] == 'Manhole Cover':
            sc = feature['subcategory']
            if sc == 'Large': 
                if not source in ['geodanmark', 'samaqua', 'kortopslag', 'fjernvarme']:
                    return False

            elif sc == 'Large Square':
                if not source in ['geodanmark', 'samaqua']:
                    return False
            
            else:
                return False
                
        # Light fixture:
        # Standing (geodanmark, energifyn) og Hanging + Ground (energifyn)
        if feature['typename'] == 'Light Fixture':
            sc = feature['subcategory']
            if sc == 'Standing': 
                if not source in ['geodanmark', 'energifyn']:
                    return False

            elif sc in ['Hanging', 'Ground']:
                if source != 'energifyn':
                    return False
            
            else:
                return False

        return True
                

    def _get_feature(self, gt_id: str = None, service_id: str = None, source: str = None):
        if gt_id == None and service_id == None:
            raise Exception('Please specify an of either type.')
    
        if gt_id != None and service_id != None:
            raise Exception('Please only specify one id.')

        data, gt = self.get_data(separated_gt=True)

        if gt_id != None:
            for ft in flatten(gt):
                if ft['id'] == gt_id:
                    return ft
            return None
                    
        for ft in flatten(data[source]):
            if ft['id'] == service_id:
                return ft
        return None

            
    def _get_stats(self):
        stats = {source: {typename: None for typename in self.all_typenames[source]} for source in self.all_sources} 
        
        for source in self.data:
            matches = self._get_matches(source)

            matched_features = [match.gt_ids[0] for match in matches]
            for ft in flatten(self.ground_truth):
                if ft['id'] in matched_features:
                    matched_features[matched_features.index(ft['id'])] = ft

            accessibilities, visibilities = self._get_validation_results(source, matches)

            for typename in self.data[source]:
                ids = [ft['id'] for ft in self.data[source][typename]]

                # Count features
                N = len(self.data[source][typename])

                # Count true positives
                tp = [ft for ft in self.data[source][typename] if any(match.is_matched(service_id=ft['id']) for match in matches)]
                tp_gt = [ft for ft in flatten(self.ground_truth) if self._should_qualify(ft, typename) and any(match.is_matched(gt_id=ft['id']) for match in matches)]

                for ft in tp_gt:
                    for match in matches:
                        if match.is_matched(gt_id=ft['id']):
                            ft['matches'] = [self._get_feature(service_id=i, source=source) for i in match.service_ids]

                # Count false positives
                fp = [ft for ft in self.data[source][typename] if not any(match.is_matched(service_id=ft['id']) for match in matches)]

                # Count false negatives
                fn = [ft for ft in flatten(self.ground_truth) if self._should_qualify(ft, typename) and not any(match.is_matched(gt_id=ft['id']) for match in matches)]

                # Get accessibility and visibility
                acc = [acc for ft, acc in zip(matched_features, accessibilities) if ft[source] in ids]
                vis = [vis for ft, vis in zip(matched_features, visibilities) if ft[source] in ids]

                # Get accuracy
                err = []
                for match in matches:
                    ft_gt = [self._get_feature(gt_id=id) for id in match.gt_ids]
                    ft_gt = [ft for ft in ft_gt if ft['fix'] == '4' or ft['note'] == 'Totalstation']

                    if len(ft_gt) == 0:
                        continue

                    for ft in ft_gt:
                        ft.to_srs(Properties.default_srs)
                    mean_gt = (sum(ft.x() for ft in ft_gt)/len(ft_gt), sum(ft.y() for ft in ft_gt)/len(ft_gt))

                    ft_s = [self._get_feature(service_id=id, source=source) for id in match.service_ids]
                    for ft in ft_s:
                        ft.to_srs(Properties.default_srs)
                    mean_s = (sum(ft.x() for ft in ft_s)/len(ft_s), sum(ft.y() for ft in ft_s)/len(ft_s))
                    
                    err.append(sqrt((mean_gt[0] - mean_s[0])**2 + (mean_gt[1] - mean_s[1])**2))

                stats[source][typename] = self.Stats(source, typename, gt_ids=[ft['id'] for ft in matched_features], service_ids=[ft[source] for ft in matched_features], amount=N, true_positives=tp, true_positives_gt = tp_gt, false_positives=fp, false_negatives=fn, accessibilities=acc, visibilities=vis, accuracies=err)

        return stats

    def __init__(self, area: str, use_exclude_property: bool = False):
        self.area = area
        self.data = self._get_data(use_exclude_property=use_exclude_property)
        self.ground_truth = self.data['groundtruth']
        del self.data['groundtruth']

        self.stats = self._get_stats()

    def get_stats(self):
        return self.stats

    def get_data(self, separated_gt: bool = False):
        if separated_gt:
            return self.data, self.ground_truth
        data = self.data
        data.update({'groundtruth': self.ground_truth})
        return data

    def get_qualifying_gt(self, source, typename):
        matches = self._get_matches(source)
        pass