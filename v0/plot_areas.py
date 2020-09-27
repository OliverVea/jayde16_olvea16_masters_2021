import matplotlib.pyplot as plt
import uuid
from random import random
from math import pi
from spider_plot import SpiderPlot
from read_csv import CSV

def avg(l: list):
    return sum(l) / len(l)

def format_data(features, fill_when_zero: bool = False):
    categories = ['Accessibility', 'Occluded Visibility', 'True Positive', 'False Positive', 'False Negative', 'Unknown']
    categories_data = {}
    for category in categories:
        categories_data[category] = {}


    for ft in features:
        for key in categories_data:
            if ft['English'] not in categories_data[key]:
                categories_data[key][ft['English']] = 0
            if ft['Category'] not in ['False Positive', 'Unknown']:
                if key == 'Accessibility':
                    categories_data[key][ft['English']] += float(ft[key]) / 100
                elif key =='Occluded Visibility':
                    categories_data[key][ft['English']] += float(ft['Accessibility']) / 100 + (1 - float(ft['Accessibility'])/100) * float(ft[key]) / 100
            if key == ft['Category']:
                categories_data[key][ft['English']] += 1

    #Average
    for key in categories_data:
        for subkey in categories_data[key]:
            if key in ['Accessibility', 'Occluded Visibility']:
                categories_data[key][subkey] /= categories_data['True Positive'][subkey] + categories_data['False Negative'][subkey]


    precision = {}
    recall = {}
    f1 = {}
    #Calculate Precision, Recall and F1
    for key in categories_data['True Positive']:
        if categories_data['True Positive'][key] > 0:
            precision[key] = categories_data['True Positive'][key] / (categories_data['True Positive'][key] + categories_data['False Positive'][key])
            recall[key] = categories_data['True Positive'][key] / (categories_data['True Positive'][key] + categories_data['False Negative'][key])
            f1[key] = 2 * precision[key] * recall[key] / (precision[key] + recall[key])
        else:
            precision[key] = 0.0
            recall[key] = 0.0
            f1[key] = 0.0
    '''
    types = list({ft['English'] for ft in features})       
    categories = list({ft['Category'] for ft in features})

    fts = {tp: {cat: features.filter(lambda ft: ft['Category'] == cat and ft['English'] == tp) for cat in categories} for tp in types}
    ftl = {tp: {cat: len(fts[tp][cat]) for cat in fts[tp]} for tp in types}

    m = {metric: {tp: 0 for tp in types if fill_when_zero} for metric in ['precision', 'recall', 'f1']}

    m['precision'].update({tp: ftl[tp]['True Positive'] / (ftl[tp]['True Positive'] + ftl[tp]['False Positive']) for tp in types if ftl[tp]['True Positive'] + ftl[tp]['False Positive'] != 0})
    m['recall'].update({tp: ftl[tp]['True Positive'] / (ftl[tp]['True Positive'] + ftl[tp]['False Negative']) for tp in types if ftl[tp]['True Positive'] + ftl[tp]['False Negative'] != 0})
    m['f1'].update({tp: 2 * m['precision'][tp] *  m['recall'][tp] / (m['precision'][tp] +  m['recall'][tp]) for tp in types if (tp in m['precision'] and tp in m['recall']) and (m['precision'][tp] + m['recall'][tp] != 0)})  

    m['accessibility'] = {tp: avg([float(ft['Accessibility']) / 100 for ft in fts[tp]['True Positive'] + fts[tp]['False Negative']]) for tp in types}
    m['visibility'] = {tp: avg([float(ft['Accessibility']) / 100 + (1 - float(ft['Accessibility']) / 100) * float(ft['Occluded Visibility']) / 100 for ft in fts[tp]['True Positive'] + fts[tp]['False Negative']]) for tp in types}

    return m['accessibility'], m['visibility'], m['precision'], m['recall'], m['f1']
    '''
    return categories_data['Accessibility'], categories_data['Occluded Visibility'], precision, recall, f1

if __name__ == '__main__':

    areas = ['Harbor', 'Park', 'SDU', 'Suburb']

    for i, area in enumerate(areas):
        csv_file = CSV(f'input/{area}_Data_Analysis.csv')
        features = csv_file.read()

        categories = ['Accessibility', 'Occluded Visibility', 'Precision', 'Recall', 'F1-value']

        data = format_data(features)

        N = len(data)
        K = len(list(data[0]))

        data_list = [[] for i in list(data[0])]
        feature_types = []

        for category in data:
            for j, val in enumerate(category.values()):
                data_list[j].append(val)
        
        for key in data[0]:
            feature_types.append(key)

        spider_plot = SpiderPlot(title=f'{area} Data', figname=f'{area}_data', autodraw=False)

        for category in categories:
            spider_plot.add_category(category, [k/(K - 1) for k in range(K)], [f'{100*k/(K - 1)}%' for k in range(K)])

        for feature_type, d in zip(feature_types, data_list):
            spider_plot.add_data(feature_type, d)

        spider_plot.draw()
    plt.show()