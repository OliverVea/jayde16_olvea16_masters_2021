import matplotlib.pyplot as plt
import uuid
from random import random
from math import pi
from jaolma.plotting.spider_plot import SpiderPlot
from jaolma.utility.read_csv import CSV
from jaolma.properties import Properties
from jaolma.utility.utility import uniform_colors, linspace


def avg(l: list):
    return sum(l) / len(l)

def format_data(features, fill_when_zero: bool = False):
    categories = ['Accessibility', 'Occluded Visibility', 'True Positive', 'False Positive', 'False Negative', 'Unknown']
    categories_data = {}
    for category in categories:
        categories_data[category] = {}


    for ft in features:
        for key in categories_data:
            if ft['Feature Tag'] not in categories_data[key]:
                categories_data[key][ft['Feature Tag']] = 0
            if ft['Category'] not in ['False Positive', 'Unknown']:
                if key == 'Accessibility':
                    categories_data[key][ft['Feature Tag']] += float(ft[key]) / 100
                elif key =='Occluded Visibility':
                    categories_data[key][ft['Feature Tag']] += float(ft['Accessibility']) / 100 + (1 - float(ft['Accessibility'])/100) * float(ft[key]) / 100
            if key == ft['Category']:
                categories_data[key][ft['Feature Tag']] += 1

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



min_tick = 0
max_tick = 1
N_tick = 5

areas = ['Harbor', 'Park', 'SDU', 'Suburb']

for i, area in enumerate(areas):
    csv_file = CSV(f'input/SpiderData/{area}_Data_Analysis.csv')
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

    spider_plot = SpiderPlot(title=f'{area} Data', figname=f'{area}_data', autodraw=False, scale_plot=True, figsize=(12,12))


    for category in categories:
        tick_values = linspace(min_tick, max_tick, N_tick)
        tick_labels = [f'{100*val:0.1f}%' for val in tick_values]

        tick_values = tick_labels = None
        spider_plot.add_category(category, tick_values, tick_labels)


    colors = uniform_colors(len(data_list))

    for feature_type, d, color in zip(feature_types, data_list, colors):
        spider_plot.add_data(Properties.get_feature_label(feature_type), d, color=color)

    spider_plot.draw()
    spider_plot.show(save_png=True)