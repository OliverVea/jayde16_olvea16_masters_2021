from numpy.core.numeric import array_equal
from jaolma.properties import Properties
from jaolma.utility.read_csv import CSV
from jaolma.utility.utility import uniform_colors#, linspace

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import use
from math import pi, ceil
import matplotlib.pyplot as plt

import pandas as pd
import PySimpleGUI as sg
import numpy as np

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

    res_dict = {'Accessibility': categories_data['Accessibility'], 
                'Visibility': categories_data['Occluded Visibility'], 
                'Precision': precision, 
                'Recall': recall, 
                'f1': f1}
    


    return res_dict

def _plot_precision(precision_sources, area, decimals: int = 3):
    fig, axs = plt.subplots(2,2, figsize=(10,10), dpi=100)
    ax = plt.subplot(111, projection='polar')
    fig.suptitle(f'Precision for {area} for all features')
    N = 0

    #Precision_sources has to contain all features for all sources
    if len(precision_sources) != 0:
        N = len(precision_sources[0])

    angles = [n / float(N) * 2 * pi for n in range(N)]   

    #Vi skal enten bruge det her
    locs, labels = plt.xticks(angles, ['' for _ in angles])
    
    #Eller det her...
    for label, angle, text in zip(labels, angles, precision_sources[0].keys()):
            x, y = label.get_position()
            temptxt = plt.text(x,y, text, transform=label.get_transform(), ha=label.get_ha(), 
            va=label.get_va(), rotation=angle*180/pi-90, size=12, color='black')


    curved_angles = []
    curved_values = []

    for an in angles:
        curved_angles.extend(np.arange(an, an + 2*np.pi/N, 0.01))

    angles += angles[:1]
    curved_angles += angles[:1]
 
    for precision_source in precision_sources:
        values = list(precision_source.values())
        values = [round(v, ndigits=decimals) for v in values]
        values += values[:1]

        #Add numbers to plots
        for idx, an in enumerate(angles[:-1]):
            plt.text(an, values[idx], str(values[idx]), color="black", size=8)

        #Create curved value intervals
        for i, val in enumerate(values[:-1]):
            curved_values.extend(np.linspace(val, values[i+1], ceil(2*np.pi/N/0.01+1))[:-1])
        curved_values += values[:1]

        ax.plot(curved_angles, curved_values, linewidth=1, linestyle='solid', label='Interval linearisation')
        ax.fill(curved_angles, curved_values, 'b', alpha=0.1)
        
    return fig
    

def _plot_recall(recall_features, sources):
    fig, axs = plt.subplots(2,2, figsize=(10,10), dpi=100)
    ax = plt.subplot(111, projection='polar')
    fig.suptitle('Something')
    #ax.plot(angles, values, linewidth=1, linestyle='solid', label='Interval linearisation')
    #ax.fill(angles, values, 'b', alpha=0.1)

def _plot_accuracy(avg_errors_features, sources):
    pass



def plot(area):
    print(f'Plotting Radar Charts for Area: {area}.')

    use("TkAgg")

    min_tick = 0
    max_tick = 1
    N_tick = 5

    precision_sources = []

    for sources in ['geodanmark']:

        csv_file = CSV(f'input/SpiderData/{area}_Data_Analysis.csv')
        features = csv_file.read()

        categories = ['Accessibility', 'Occluded Visibility', 'Precision', 'Recall', 'F1-value']

        data = format_data(features)

        precision_sources.append(data['Precision'])

        fig = _plot_precision(precision_sources, area)
        
        #N = len(data)
        #K = len(list(data[0]))

        #data_list = [[] for i in list(data[0])]
        #feature_types = []

        #for category in data:
        #    for j, val in enumerate(category.values()):
        #        data_list[j].append(val)

        #for key in data[0]:
        #    feature_types.append(key)

    #spider_plot = SpiderPlot(title=f'{area} Data', figname=f'{area}_data', autodraw=False, scale_plot=True, figsize=(12,12))

    #for category in categories:
    #    tick_values = linspace(min_tick, max_tick, N_tick)
    #    tick_labels = [f'{100*val:0.1f}%' for val in tick_values]

    #    tick_values = tick_labels = None
    #    spider_plot.add_category(category, tick_values, tick_labels)


    #colors = uniform_colors(len(data_list))

    #for feature_type, d, color in zip(feature_types, data_list, colors):
    #    spider_plot.add_data(Properties.get_feature_label(feature_type), d, color=color)

    #spider_plot.draw()
    #spider_plot.show(save_png=True)


    '''
    values = [10, 0, 10,0,20, 20,15,5,10]
    angles = [0,45,90,135,180, 225, 270, 315,360]

    angles = [y/180*np.pi for x in [np.arange(x, x+45,0.1) for x in angles[:-1]] for y in x]
    values = [y for x in [np.linspace(x, values[i+1], 451)[:-1] for i, x in enumerate(values[:-1])] for y in x]
    angles.append(360/180*np.pi)
    values.append(values[0])

    values_ = [15, 0, 20,0,5, 10,15,5,15]
    angles_ = [0,45,90,135,180, 225, 270, 315,360]

    angles_ = [y/180*np.pi for x in [np.arange(x, x+45,0.1) for x in angles_[:-1]] for y in x]
    values_ = [y for x in [np.linspace(x, values_[i+1], 451)[:-1] for i, x in enumerate(values_[:-1])] for y in x]
    angles_.append(360/180*np.pi)
    values_.append(values_[0])


    #t = np.arange(0, 3, .01)
    fig, axs = plt.subplots(2,2, figsize=(10,10), dpi=100)
    ax = plt.subplot(111, projection='polar')
    fig.suptitle('Something')
    ax.plot(angles, values, linewidth=1, linestyle='solid', label='Interval linearisation')
    ax.fill(angles, values, 'b', alpha=0.1)
    ax.plot(angles_, values_, linewidth=1, linestyle='solid', label='Interval linearisation')
    ax.fill(angles_, values_, 'b', alpha=0.1)
    '''

    pretty_area = list(Properties.areas).index(area)
    pretty_area = Properties.areas_pretty[pretty_area]

    title = f'{pretty_area}'
    export = sg.Button('Export')
    back = sg.Button('Back')

    col = [[export, back]]

    checkboxes = sg.Column(col, vertical_alignment='top')

    size = (1000,1000)

    graph = sg.Graph(canvas_size=size, graph_bottom_left=(0,0), graph_top_right=size, key='Radar', enable_events=True)

    layout = [
        [checkboxes, graph]
    ]
    
    window = sg.Window(title, layout, finalize=True)

    figure_canvas_agg = FigureCanvasTkAgg(fig, window["Radar"].TKCanvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)

    event, values = window.read()
    
    window.close()

    return event

if __name__ == '__main__':
    sg.theme('DarkGrey2')
    plot('park')