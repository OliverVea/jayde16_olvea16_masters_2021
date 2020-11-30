import main_plot_area

from jaolma.properties import Properties
from jaolma.gis.wmts import WMTS
from jaolma.gis.wfs import Feature
from jaolma.utility.utility import transpose, printe, prints, Color

from jaolma.gui import simple_dropdown

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import use

import matplotlib.pyplot as plt

import numpy as np
from time import sleep

import pandas as pd
import PySimpleGUI as sg
import os

from PIL import Image, ImageDraw

from random import choice
from math import sqrt

sg.theme('DarkGrey2')



def pick_area() -> str:
    return simple_dropdown('Select Area', list(Properties.areas))

actions = {}
def pick_action() -> str:
    return simple_dropdown('Select Action', list(actions))


#JAKOB WAS HERE
def plot_radar(area):
    # TODO: Implement this.
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


def get_data(area):
    # TODO: Implement this.
    print(f'Getting Data for Area: {area}.')
    pass

def analyse_area(area):
    # TODO: Implement this.
    pass

def analyse_feature(typename):
    # TODO: Implement this.
    pass

actions['Plot Area'] = main_plot_area.plot
actions['Plot Radar Charts for Area'] = plot_radar
actions['Get Data for Area'] = get_data
actions['Analyse an area'] = analyse_area
actions['Analyse a feature type'] = analyse_feature

while True:
    area = pick_area()

    if area == None:
        exit()

    action = pick_action()

    if action in (None, ''):
        exit()

    event = actions[action](area)

    if event != 'Back':
        break