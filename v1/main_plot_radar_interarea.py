from jaolma.properties import Properties
from jaolma.utility.read_csv import CSV
from jaolma.utility.utility import uniform_colors, linspace

from matplotlib import use
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

    return categories_data['Accessibility'], categories_data['Occluded Visibility'], precision, recall, f1

def _plot_precision(precision_areas, sources):
    pass

def _plot_recall(recall_areas, sources):
    pass

def _plot_accuracy(avg_errors_areas, sources):
    pass



def plot(area):
    print(f'Plotting Radar Charts for Area: {area}.')

    use("TkAgg")

    min_tick = 0
    max_tick = 1
    N_tick = 5

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

    #spider_plot = SpiderPlot(title=f'{area} Data', figname=f'{area}_data', autodraw=False, scale_plot=True, figsize=(12,12))

    for category in categories:
        tick_values = linspace(min_tick, max_tick, N_tick)
        tick_labels = [f'{100*val:0.1f}%' for val in tick_values]

        tick_values = tick_labels = None
        spider_plot.add_category(category, tick_values, tick_labels)


    #colors = uniform_colors(len(data_list))

    for feature_type, d, color in zip(feature_types, data_list, colors):
        spider_plot.add_data(Properties.get_feature_label(feature_type), d, color=color)

    #spider_plot.draw()
    #spider_plot.show(save_png=True)



    df = pd.DataFrame({'measure':[10, 0, 10,0,20, 20,15,5,10], 'angle':[0,45,90,135,180, 225, 270, 315,360]})
    values = [10, 0, 10,0,20, 20,15,5,10]
    angles = [0,45,90,135,180, 225, 270, 315,360]

    angles = [y/180*np.pi for x in [np.arange(x, x+45,0.1) for x in angles[:-1]] for y in x]
    values = [y for x in [np.linspace(x, values[i+1], 451)[:-1] for i, x in enumerate(values[:-1])] for y in x]
    angles.append(360/180*np.pi)
    values.append(values[0])


    t = np.arange(0, 3, .01)
    fig, axs = plt.subplots(2,2, figsize=(10,10), dpi=100)
    ax = plt.subplot(111, projection='polar')
    ax.plot(angles, values, linewidth=1, linestyle='solid', label='Interval linearisation')
    ax.fill(angles, values, 'b', alpha=0.1)

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

def plot(area):
    from jaolma.plotting.spider_plot import spider_plot

    fig = spider_plot(
        'DND Class Stats',
        labels=['Strength', 'Dexterity', 'Intelligence', 'Speed', 'Luck'],
        silhouettes={'warrior': [15, 13, 9, 11, 10], 'thief': [9, 17, 13, 14, 15], 'mage': [3, 8, 18, 7, 12]},
        circle_label=True,
        circle_label_decimals=0,
        #scale_type='total_both',
        #axis_value_labels=False
    )

    size = (1000,1000)

    graph = sg.Graph(canvas_size=size, graph_bottom_left=(0,0), graph_top_right=size, key='Radar', enable_events=True)

    layout = [
        [graph]
    ]

    window = sg.Window('fisk', layout, finalize=True)

    figure_canvas_agg = FigureCanvasTkAgg(fig, window["Radar"].TKCanvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)

    event, values = window.read()

if __name__ == '__main__':
    sg.theme('DarkGrey2')
    plot('downtown')