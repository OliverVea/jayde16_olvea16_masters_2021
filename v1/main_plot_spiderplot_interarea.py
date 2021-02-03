from jaolma.properties import Properties
from jaolma.plotting.spider_plot import spider_plot
from jaolma.gui import simple_dropdown
from jaolma.data_treatment.data_treatment import GISData
from jaolma.utility.utility import uniform_colors

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import use
import matplotlib.pyplot as plt

import PySimpleGUI as sg
import numpy as np

def pick_plottype(plottypes) -> str:
    return simple_dropdown('Select Plot', list(plottypes))

def _get_stats(area):
    
    title = 'Feature Stats'
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
            silhouettes[label].append(round(ft.get_accuracy(),2))
            silhouettes[label].append(round(ft.get_visibility(),1))
            silhouettes[label].append(round(ft.get_accessibility(),1))
            silhouettes[label].append(len(ft.true_positives))
        
    return silhouettes, labels, sources, title

def _get_amount_gt():
    
    title = 'Feature count across areas'
    #labels=['Precision', 'Recall', 'Error', 'Visibility', 'Accessibility', 'True Positives']
    labels = ['Tree', 'Light Fixture', 'Downspout Grille', 'Manhole Cover', 'Bench', 'Trash Can']

    silhouettes = {}
    source = 'groundtruth'

    for area in Properties.areas:
        silhouettes[area] = [0] * len(labels)
        gisdata = GISData(area)
        data = gisdata.get_data()

        for i, _ in enumerate(silhouettes[area]):
            if labels[i] in data[source]:        
                silhouettes[area][i] = len(data[source][labels[i]])
        
    return silhouettes, labels, title

def _plot_recall(recall_features, sources):
    fig, axs = plt.subplots(2,2, figsize=(10,10), dpi=100)
    ax = plt.subplot(111, projection='polar')
    fig.suptitle('Something')
    #ax.plot(angles, values, linewidth=1, linestyle='solid', label='Interval linearisation')
    #ax.fill(angles, values, 'b', alpha=0.1)

def _plot_accuracy(avg_errors_features, sources):
    pass



def plot(plottype):
    if plottype in [None, '']:
        return plottype

    if plottype == 'plot_stats_':
        print('Plotting Radar Chart with stats for each source across areas.')
        silhouettes, labels, sources, title = _get_stats()
    elif plottype == 'plot_amount_gt':
        silhouettes, labels, title = _get_amount_gt()
    else:
        pass
        silhouettes, labels, sources, title = _get_stats()

    use("TkAgg")
    
    #plottypes = {'Plot Precision, Recall, Accuracy, Visibility, Accessibility and amount for all features.': 'plot_stats'}

    #plottype = pick_plottype(plottypes.keys())

    colors = uniform_colors(len(silhouettes))

    inputs = {}

    #title = f'{title}'
    export = sg.Button('Export')
    back = sg.Button('Back')

    col = [[export, back]]

    i = 0
    for area in list(Properties.areas):
        color = colors[i]
        label = list(silhouettes.keys())[i]

        col.append([sg.Checkbox(label, text_color = color, key=area, enable_events=True)])
        inputs[len(inputs)] = {'type': 'checkbox', 'typename': area}
        i += 1
    
    checkboxes = sg.Column(col, vertical_alignment='top')

    size = (1000,1000)

    graph = sg.Graph(canvas_size=size, graph_bottom_left=(0,0), graph_top_right=size, key='Radar', enable_events=True)

    layout = [
        [checkboxes, graph]
    ]
    
    window = sg.Window(title, layout, finalize=True)

    #Instantiate figure_canvas_agg to allow for destruction in infinite loop.
    fig = spider_plot('', labels=labels, silhouettes=silhouettes)
    figure_canvas_agg = FigureCanvasTkAgg(fig, window["Radar"].TKCanvas)

    while True:
        event, values = window.read()
        
        #Check for close or back event
        if event == sg.WIN_CLOSED or event == 'Back':
            break

        #Set types to all types that are checked on
        types = set([inputs[i]['typename'] for i in inputs if values[inputs[i]['typename']]])

        #Destroy current canvas to allow for a new plot
        figure_canvas_agg.get_tk_widget().destroy()

        #Filter which silhouettes to plot depending on the current checkboxes
        plot_silhouettes = dict((k, v) for k, v in zip(silhouettes.keys(), silhouettes.values()) if k in types)
        
        if len(plot_silhouettes) > 0:

            #Filter colors to fit the checkboxes
            plot_colors = [colors[list(silhouettes.keys()).index(key)] for key in plot_silhouettes.keys()]

            #Set minimum and maximum of all axes
            #axis_min = [0,0,0,0,0,0]
            #axis_max = [100, 100, max(0.1, max(v[2] for v in plot_silhouettes.values())), 100, 100, max(0.1, max(v[5] for v in plot_silhouettes.values()))]

            fig = spider_plot(
            title,
            labels=labels,
            silhouettes=plot_silhouettes,
            #scale_type='total_max',
            axis_ticks=5,
            axis_value_labels=False,
            #axis_min=axis_min,
            #axis_max=axis_max,
            #reversed_axes=[False, False, True, False, False, False],
            silhouette_line_color=plot_colors,
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
    plot('plot_amount_gt')