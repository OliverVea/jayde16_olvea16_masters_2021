import main_plot_area
import main_plot_spiderplot_area
import main_plot_spiderplot

from jaolma.properties import Properties
from jaolma.utility.utility import printe, prints

from jaolma.gui import simple_dropdown

import PySimpleGUI as sg
import jaolma.gis.wfs as wfs
import os, pynmea2

def load_route(filename):
    if not os.path.exists(filename):
        return None
    with open(filename, 'r') as f:
        nmea_file = f.readlines()

    fts = []
    fixes = []
    for line in nmea_file[1:]:
        line = ','.join(line.strip().split(',')[2:])
        nmea_msg = pynmea2.parse(line)
        if nmea_msg.sentence_type != 'GGA':
            continue
        ft = wfs.Feature((nmea_msg.latitude, nmea_msg.longitude), 'EPSG:4326')
        fts.append(ft)
        fixes.append(nmea_msg.gps_qual)

    collection = wfs.Collection('','',fts,'EPSG:4326')
    collection.to_srs('EPSG:25832')
    route = [[ft.x(), ft.y(), fix] for ft, fix in zip(collection.features, fixes)]
    return route


sg.theme('DarkGrey2')

def pick_action1() -> str:
    return simple_dropdown('Select Area', list(Properties.areas) + ['Plot Stats', 'Plot Amount of Features (groundtruth)'])

actions = {}
def pick_action2() -> str:
    return simple_dropdown('Select Action', list(actions))

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
actions['Plot Radar Charts for Area'] = main_plot_spiderplot_area.plot
actions['Get Data for Area'] = get_data
actions['Analyse an area'] = analyse_area
actions['Analyse a feature type'] = analyse_feature

route = load_route(filename='files/gps_routes/2021-04-23_11-01-38.csv')


while True:
    action1 = pick_action1()

    if action1 == None:
        break

    if action1 == 'Plot Stats':
        event = main_plot_spiderplot.plot('plot_stats')

    elif action1 == 'Plot Amount of Features (groundtruth)':
        event = main_plot_spiderplot.plot('plot_amount_gt')

    else:
        action2 = pick_action2()

        if action2 in (None, ''):
            break

        if action2 == 'Plot Area':
            event = actions[action2](action1, route=route)
        else:
            event = actions[action2](action1)

        if event != 'Back':
            break