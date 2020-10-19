import matplotlib.pyplot as plt
import uuid
from random import random
from math import pi
from jaolma.plotting.spider_plot import SpiderPlot
from jaolma.utility.read_csv import CSV
from jaolma.properties import Properties
from jaolma.utility.utility import uniform_colors, linspace, transpose


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
    
    return categories_data['Accessibility'], categories_data['Occluded Visibility'], precision, recall, f1


categories = Properties.feature_properties

min_tick = 0
max_tick = 1
N_tick = 5

areas = ['Harbor', 'Park', 'SDU', 'Suburb']

N = len(areas)
K = len(categories)

spider_plot = SpiderPlot(title='Features Across Areas', figname='Features Across Areas', autodraw=False, scale_plot=False, figsize=(12,12))


for category in categories:
    tick_values = linspace(min_tick, max_tick, N_tick)
    tick_labels = [f'{100*val:0.1f}%' for val in tick_values]

    tick_values = tick_labels = None
    spider_plot.add_category(Properties.get_feature_label(category), tick_values, tick_labels)


colors = uniform_colors(N)

all_data = []

for area in areas:

    csv_file = CSV(f'input/SpiderData/{area}_Data_Analysis.csv')
    features = csv_file.read()

    for cat in categories:
        categories[cat]['amount'] = 0

    for cat in categories:
        for ft in features:
            if ft['Feature Tag'] == cat:
                categories[cat]['amount'] += 1

    data_list = []
    for cat in categories:
        data_list.append(categories[cat]['amount'])

    data_list = [d/max(data_list) for d in data_list]
    
    all_data.append(data_list)

#all_data = transpose(all_data)

for area, color, d in zip(areas, colors, all_data):
    spider_plot.add_data(area, d, color=color)

spider_plot.draw()
spider_plot.show(save_png=False)

