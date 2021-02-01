from jaolma.properties import Properties
from jaolma.plotting.spider_plot import spider_plot
from jaolma.gui import simple_dropdown
from jaolma.gather_data import GISData
from jaolma.utility.utility import uniform_colors

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import use
import matplotlib.pyplot as plt

import PySimpleGUI as sg
import numpy as np

def pick_plottype(plottypes) -> str:
    return simple_dropdown('Select Plot', list(plottypes))

def _get_stats(area):
    
    labels=['Precision', 'Recall', 'Error', 'Visibility', 'Accessibility', 'True Positives']

    silhouettes = {}
    sources = {}

    data = GISData(area)

    stats = data.get_stats()

    for source, features in zip(stats.keys(), stats.values()):
        sources[source] = []
        for ft_name, ft in zip(features.keys(), features.values()):
            if ft == None or ft.get_recall() == None:
                continue
            label = Properties.feature_properties[ft_name]['label']
            sources[source].append(label)
            silhouettes[label] = []
            silhouettes[label].append(round(ft.get_precision()*100,1))
            silhouettes[label].append(round(ft.get_recall()*100,1))
            silhouettes[label].append(round(1/ft.get_accuracy(),2))
            silhouettes[label].append(round(ft.get_visibility(),1))
            silhouettes[label].append(round(ft.get_accessibility(),1))
            silhouettes[label].append(len(ft.true_positives))
        
    return silhouettes, labels, sources

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

    
    plottypes = {'Plot Precision, Recall, Accuracy, Visibility, Accessibility and amount for all features.': 'plot_stats'}

    plottype = pick_plottype(plottypes.keys())

    if plottype in [None, '']:
        return plottype

    if plottypes[plottype] == 'plot_stats':
        silhouettes, labels, sources = _get_stats(area)
    else:
        silhouettes, labels, sources = _get_stats(area)

    colors = uniform_colors(len(silhouettes))

    inputs = {}

    pretty_area = list(Properties.areas).index(area)
    pretty_area = Properties.areas_pretty[pretty_area]

    title = f'{pretty_area}'
    export = sg.Button('Export')
    back = sg.Button('Back')

    col = [[export, back]]

    i = 0
    for source in sources.keys():
        col.append([sg.Text(source.capitalize(), enable_events=True)])

        for feature in list(sources[source]):
            color = colors[i]
            label = list(silhouettes.keys())[i]

            col.append([sg.Checkbox(label, text_color = color, key=feature, enable_events=True)])
            inputs[len(inputs)] = {'type': 'checkbox', 'source': source, 'typename': feature}
            i += 1
    
    checkboxes = sg.Column(col, vertical_alignment='top')

    size = (1000,1000)

    graph = sg.Graph(canvas_size=size, graph_bottom_left=(0,0), graph_top_right=size, key='Radar', enable_events=True)

    layout = [
        [checkboxes, graph]
    ]
    
    window = sg.Window(title, layout, finalize=True)

    fig = spider_plot(
        'DND Class Stats',
        labels=labels,
        silhouettes=silhouettes,
        #circle_label=False,
        #circle_label_decimals=0,
        #axis_value_labels=axis_value_labels,
        #circle_n=5,
        scale_type='set',
        #axis_min=axis_min,
        #axis_max=axis_max,
        #silhouette_line_color=['y', (1, 0.6, 0.6), 'teal'],
        #silhouette_fill_color=[(1, 0.6, 0.6), 'teal', 'y'],
        silhouette_line_size=1.5,
        silhouette_line_style='-.',
        silhouette_fill_alpha=0.25,
    )

    
    figure_canvas_agg = FigureCanvasTkAgg(fig, window["Radar"].TKCanvas)
    #figure_canvas_agg.draw()
    #figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)

    while True:
        event, values = window.read()
        
        if event == sg.WIN_CLOSED or event == 'Back':
            break

        types = set([inputs[i]['typename'] for i in inputs if values[inputs[i]['typename']]])

        if type(event) == str and event.lower() in sources:
            source = event.lower()

            source_types = list(sources[source])

            if all(typename in types for typename in source_types):
                for typename in source_types:
                    cb = window.find(typename)
                    cb.update(value=False)
                    types.remove(typename)
            else:
                for typename in source_types:
                    cb = window.find(typename)
                    cb.update(value=True)
                    types.add(typename)

        figure_canvas_agg.get_tk_widget().destroy()

        plot_silhouettes = dict((k, v) for k, v in zip(silhouettes.keys(), silhouettes.values()) if k in types)
        if len(plot_silhouettes) > 0:
            fig = spider_plot(
            'DND Class Stats',
            labels=labels,
            silhouettes=plot_silhouettes,
            #circle_label=False,
            #circle_label_decimals=0,
            #axis_value_labels=axis_value_labels,
            #circle_n=5,
            scale_type='axis_max',
            #axis_min=axis_min,
            #axis_max=axis_max,
            #silhouette_line_color=['y', (1, 0.6, 0.6), 'teal'],
            #silhouette_fill_color=[(1, 0.6, 0.6), 'teal', 'y'],
            silhouette_line_size=1.5,
            silhouette_line_style='-.',
            silhouette_fill_alpha=0.25,
            )

            figure_canvas_agg = FigureCanvasTkAgg(fig, window["Radar"].TKCanvas)
            figure_canvas_agg.draw()
            figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)


    window.close()

    return event

if __name__ == '__main__':
    sg.theme('DarkGrey2')
    plot('downtown')