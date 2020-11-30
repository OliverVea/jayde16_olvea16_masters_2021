from jaolma.properties import Properties
from jaolma.gui.properties_box import PropertiesBox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import use

import matplotlib.pyplot as plt

import pandas as pd
import PySimpleGUI as sg
import numpy as np

#JAKOB WAS HERE
def plot(area):
    print(f'Plotting Radar Charts for Area: {area}.')

    use("TkAgg")

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

    properties = PropertiesBox()

    layout = [
        [checkboxes, graph, properties.get_properties()]
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
    plot('downtown')