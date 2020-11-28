from jaolma.properties import Properties
from jaolma.gis.wmts import WMTS
from jaolma.gis.wfs import Feature
from jaolma.utility.utility import transpose, printe, prints, Color

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

class Plot_Image:
    def __init__(self, size: tuple, area: str, data: dict, tile_matrix: int = 13, background_path: str = 'files/gui/background.png', image_path: str = 'files/gui/image.png'):
        self.wmts = WMTS(use_login=True,
            url='https://services.datafordeler.dk/GeoDanmarkOrto/orto_foraar_wmts/1.0.0/WMTS?',
            username='VCSWRCSUKZ',
            password='hrN9aTirUg5c!np',
            layer='orto_foraar_wmts',
            tile_matrix_set='KortforsyningTilingDK')

        self.size = size
        self.area = area

        self.c = Properties.areas[area]
        self.c.to_srs(Properties.default_srs)

        self.tile_matrix = tile_matrix

        self.backgound_path = background_path
        self.image_path = image_path

        self.background = self.wmts.get_map(style='default', tile_matrix=tile_matrix, center=self.c, screen_width=size[0], screen_height=size[1])
        self.background.save(self.backgound_path)

        self.dpm = self.wmts.dpm(self.tile_matrix)

        self.data = {}
        for source in data:
            types = data[source]
            self.data[source] = {}
            for typename in types:
                features = types[typename]

                for feature in features:
                    feature.to_srs(Properties.default_srs)

                features = [feature - self.c for feature in features]

                for feature in features:
                    feature['plot_x'] = feature.x() * self.dpm + size[0] / 2
                    feature['plot_y'] = -feature.y() * self.dpm + size[1] / 2
                    pass

                if any([abs(feature.x()) > 110 or abs(feature.y()) > 110 for feature in features]):
                    printe(f'Features from source \'{source}\' with label \'{Properties.feature_properties[typename]["label"]}\' not loaded correctly. Omitting them.', tag='Warning')
                    self.data[source][typename] = [feature for feature in features if (abs(feature.x()) <= 110 or abs(feature.y()) <= 110)]

                else:
                    self.data[source][typename] = features

        pass

    def get_image(self, types: list, show_circle: bool = True, selected: str = None, show_annotations: bool = True, r: float = 3):
        with Image.open(self.backgound_path) as im:
            draw = ImageDraw.Draw(im)

            features = []
            for source in self.data:
                for typename in self.data[source]:
                    if typename in types:
                        c = Properties.feature_properties[typename]['color']
                        for f in self.data[source][typename]:
                            x, y = f['plot_x'], f['plot_y']

                            features.append({'start': (x, y), 'annotation': (x + 3, y + 3), 'feature': f, 'color': c, 'type': typename})

            n, m = 20, 0.5

            for _ in range(n):
                for ft1 in features:
                    x1, y1 = ft1['annotation']

                    x, y = 0, 0

                    i = 0

                    for ft2 in features:
                        x2, y2 = ft2['annotation']
                        for x2, y2 in zip((x2, ft2['start'][0]), (y2, ft2['start'][1])):
                            if ft1['feature']['id'] == ft2['feature']['id']:
                                continue

                            x2, y2 = ft2['annotation']

                            dx, dy = x2 - x1, y2 - y1
                            d = sqrt(dx**2 + dy**2)

                            if d > 10:
                                continue

                            i += 1

                            x, y = x + dx, y + dy

                    if i > 0:
                        x1 -= 1/n * 1/m * (x / i)
                        y1 -= 1/n * 1/m * (y / i)

                    ft1['annotation'] = (x1, y1)

            for ft in features:
                color = Color(ft['color'])

                outline = color * 0.75
                fill = ft['color']

                x, y = ft['start']
                xy = [(x - r, y - r), (x + r, y + r)]

                if selected == ft['feature']['id']:
                    outline = 'red'

                draw.ellipse(xy=xy, fill=fill, outline=outline)

            for ft in features: 
                if selected == ft['feature']['id']:
                    draw.text(xy=[ft['annotation'][0], ft['annotation'][1]], text=f'{ft["feature"]["n"]}', fill='red')
                else:
                    if Properties.feature_properties[ft['feature']['typename']]['origin'] == 'gnss':
                        draw.text(xy=[ft['annotation'][0], ft['annotation'][1]], text=f'{ft["feature"]["n"]}', fill=ft['color'])
                    else:
                        draw.text(xy=[ft['annotation'][0], ft['annotation'][1]], text=f'{ft["feature"]["n"]}')

            if show_circle:
                x0 = (self.size[0] / 2 - Properties.radius * self.dpm, self.size[1] / 2 - Properties.radius * self.dpm)
                x1 = (self.size[0] / 2 + Properties.radius * self.dpm, self.size[1] / 2 + Properties.radius * self.dpm)

                draw.ellipse([x0, x1], outline='#ff0000')

            im.save(self.image_path)

        return self.image_path

class PropertiesBox:
    def __init__(self):
        self.prop_text = sg.Text('Properties', font=('Any', 11, 'bold'))
        self.init_text = sg.Text('Press a feature to show it in this window.')

        self.id = '23211512'

        cw, ch = 400, 1000

        self.attributes = [[sg.Text('', visible=False, key=f'{self.id}_att_{i}', font=('Any', 10), size=(cw, None), auto_size_text=False)] for i in range(50)]

        self.properties = sg.Column([[self.prop_text]] + self.attributes + [[self.init_text]], size=(cw, ch), vertical_alignment='top')
        
        self.visible = True


    def get_properties(self):
        return self.properties

    def set_attributes(self, window, attributes):
        self.init_text.update(visible=False)

        for i, attribute in enumerate(attributes):
            attribute_name = window.find(f'{self.id}_att_{i}')
            attribute_name.update(value=f'{attribute}: {attributes[attribute]}', visible=True)

        for i in range(50 - len(attributes)):
            i += len(attributes)
            attribute_name = window.find(f'{self.id}_att_{i}')
            attribute_name.update(visible=False)

def simple_dropdown(title: str, values: list):
    dd = sg.DropDown(values, default_value=values[0])
    bo = sg.Button('OK')
    bc = sg.Button('Cancel')

    layout = [[dd, bo, bc]]

    window = sg.Window(title, layout)

    while True:
        event, values = window.read()

        if event == 'Cancel' or event == sg.WIN_CLOSED:
            value = None
            break

        if event == 'OK':
            value = values[0]
            break

    window.close()
    return value

def pick_area() -> str:
    return simple_dropdown('Select Area', list(Properties.areas))

actions = {}
def pick_action() -> str:
    return simple_dropdown('Select Action', list(actions))

def get_area_data(area: str):    
    path = 'files/areas'
    files = [file for file in os.listdir(path) if os.path.split(file)[-1][:-4].split('_')[1] == area and os.path.split(file)[-1][:-4].split('_')[2] != '0']
    files = {file.split('_')[0]: pd.read_csv(f'{path}/{file}') for file in files}
    
    result = {}
    for source, data in zip(files.keys(), files.values()):
        features = {}
        for n, row in data.iterrows():
            row = dict(row)

            row['n'] = n

            geometry = row['geometry'].split(';')[1].split(',')
            geometry = [g[1:-1] for g in geometry]
            geometry = transpose([[float(v) for v in g.split(',')] for g in geometry])

            if len(geometry) == 1:
                geometry = geometry[0]
            else:
                geometry = [[pos[0] for pos in geometry], [pos[1] for pos in geometry]] 

            tag = row['geometry'].split(';')[0]

            del row['geometry']

            feature = Feature(geometry, srs=Properties.default_srs, tag=tag, attributes=row)
            features.setdefault(row['typename'], []).append(feature)
        result[source] = features

    return result

def plot(area):
    inputs = {}

    pretty_area = list(Properties.areas).index(area)
    pretty_area = Properties.areas_pretty[pretty_area]

    title = f'{pretty_area}'
    export = sg.Button('Export')
    back = sg.Button('Back')

    data = get_area_data(area)
    sources = [source for source in data]

    col = [[export, back]]

    fp = Properties.feature_properties
    for source in sources:
        col.append([sg.Text(source.capitalize(), enable_events=True)])

        for feature in list(data[source]):
            if fp[feature]['origin'] != source:
                continue

            color = fp[feature]['color']
            label = fp[feature]['label']

            col.append([sg.Checkbox(label, text_color = color, key=feature, enable_events=True)])
            inputs[len(inputs)] = {'type': 'checkbox', 'source': source, 'typename': feature}

    checkboxes = sg.Column(col, vertical_alignment='top')

    size = (1001,1001)

    image_object = Plot_Image(size=size, area=area, data=data)

    graph = sg.Graph(canvas_size=size, graph_bottom_left=(0,0), graph_top_right=size, key='Click', enable_events=True)

    properties = PropertiesBox()

    layout = [
        [checkboxes, graph, properties.get_properties()]
    ]

    window = sg.Window(title, layout)
    window.finalize()

    graph.DrawImage(image_object.get_image([]), location=(0, size[1]))

    selected = None

    while True:
        event, values = window.read()

        print(event, values)

        if event == sg.WIN_CLOSED or event == 'Back':
            break

        types = set([inputs[i]['typename'] for i in inputs if values[inputs[i]['typename']]])

        if type(event) == str and event.lower() in sources:
            source = event.lower()


            source_types = list(data[source])

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

        if event == 'Click':
            features = []
            for source in sources:
                for typename in image_object.data[source]:
                    if typename in types:
                        features.extend(image_object.data[source][typename])

            x, y = values['Click']
            y = size[1] - y

            features = [{'d': ((ft['plot_x'] - x)**2 + (ft['plot_y'] - y)**2), 'feature': ft} for ft in features]

            selected = None
            if len(features) > 0:
                ft = min(features, key=lambda ft: ft['d'])
                feature = ft['feature']
                
                attributes = {}
                if ft['d'] < 7**2:
                    selected = feature['id']
                    for key, val in zip(feature.attributes.keys(), feature.attributes.values()):
                        t = type(val)

                        if not t in (int, str, float) or key == 'Unnamed: 0' or str(val) in ('nan', 'None'):
                            continue
                        
                        attributes[key] = val

                properties.set_attributes(window, attributes)

        graph.DrawImage(image_object.get_image(types=types, selected=selected), location=(0, size[1]))

    window.close()

    return event

actions['Plot Area'] = plot

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

actions['Plot Radar Charts for Area'] = plot_radar


def get_data(area):
    # TODO: Implement this.
    print(f'Getting Data for Area: {area}.')
    pass
actions['Get Data for Area'] = get_data

def analyse_area(area):
    # TODO: Implement this.
    pass
actions['Analyse an area'] = analyse_area

def analyse_feature(typename):
    # TODO: Implement this.
    pass
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