from jaolma.properties import Properties
from jaolma.gis.wmts import WMTS
from jaolma.gis.wfs import Feature
from jaolma.utility.utility import transpose, printe, prints, Color

import pandas as pd
import PySimpleGUI as sg
import os

from PIL import Image, ImageDraw

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
                    self.data[source][typename] = []

                else:
                    self.data[source][typename] = features

        pass

    def get_image(self, types: list, draw_circle: bool = True):
        with Image.open(self.backgound_path) as im:
            draw = ImageDraw.Draw(im)

            for source in self.data:
                for typename in self.data[source]:
                    if typename in types:
                        c = Properties.feature_properties[typename]['color']
                        color = Color(c)

                        outline = color * 0.75
                        fill = c

                        for f in self.data[source][typename]:
                            xy = [(f['plot_x'] - 3, f['plot_y'] - 3), (f['plot_x'] + 3, f['plot_y'] + 3)]
                            draw.ellipse(xy=xy, fill=fill, outline=outline)

                            # TODO: Annotate points.
                            pass

            if draw_circle:
                x0 = (self.size[0] / 2 - Properties.radius * self.dpm, self.size[1] / 2 - Properties.radius * self.dpm)
                x1 = (self.size[0] / 2 + Properties.radius * self.dpm, self.size[1] / 2 + Properties.radius * self.dpm)

                draw.ellipse([x0, x1], outline='#ff0000')

            im.save(self.image_path)

        return self.image_path


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

    title = sg.Text(f'Plot: {area}')
    back = sg.Button('Back')
    draw = sg.Button('Draw')

    data = get_area_data(area)
    sources = [source for source in data]

    col = []

    fp = Properties.feature_properties
    for source in sources:
        col.append([sg.Text(source)])

        for feature in list(data[source]):
            if fp[feature]['origin'] != source:
                continue

            color = fp[feature]['color']
            label = fp[feature]['label']

            col.append([sg.Checkbox(label, text_color = color)])
            inputs[len(inputs)] = {'type': 'checkbox', 'source': source, 'typename': feature}

    checkboxes = sg.Column(col)

    size = (1000,1000)

    image_object = Plot_Image(size=size, area=area, data=data)

    graph = sg.Graph(canvas_size=size, graph_bottom_left=(0,0), graph_top_right=size, key='Click', enable_events=True)

    layout = [
        [title, draw, back],
        [checkboxes, graph]
    ]

    window = sg.Window(title, layout)
    window.finalize()

    graph.DrawImage(image_object.get_image([]), location=(0, size[1]))

    while True:
        event, values = window.read()

        print(event, values)

        if event == sg.WIN_CLOSED or event == 'Back':
            break

        if event == 'Draw':
            types = [inputs[i]['typename'] for i in inputs if values[i]]
            graph.DrawImage(image_object.get_image(types=types), location=(0, size[1]))

        if event == 'Click':
            # TODO: Identify clostest point and write some information in panel.
            pass

    window.close()

    return event

actions['Plot Area'] = plot

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