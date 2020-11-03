from jaolma.properties import Properties
from jaolma.gis.wmts import WMTS
from jaolma.gis.wfs import Feature
from jaolma.utility.utility import transpose, printe, prints, Color

import pandas as pd
import PySimpleGUI as sg
import os

from PIL import Image, ImageDraw

from random import choice

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

    def get_image(self, types: list, show_circle: bool = True, selected: str = None, show_annotations: bool = True):
        with Image.open(self.backgound_path) as im:
            draw = ImageDraw.Draw(im)

            i = 0

            for source in self.data:
                for typename in self.data[source]:
                    if typename in types:
                        c = Properties.feature_properties[typename]['color']
                        color = Color(c)

                        outline = color * 0.75
                        fill = c

                        for f in self.data[source][typename]:
                            xy = [(f['plot_x'] - 3, f['plot_y'] - 3), (f['plot_x'] + 3, f['plot_y'] + 3)]

                            if selected == f['id']:
                                draw.ellipse(xy=xy, fill=fill, outline='red')
                            else:
                                draw.ellipse(xy=xy, fill=fill, outline=outline)

                            draw.text(xy=[f['plot_x'] + 3, f['plot_y'] + 3], text=f'{i}')
                            i += 1

                            # TODO: Annotate points.
                            pass

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

        self.attributes = [[sg.Text('', visible=False, key=f'{self.id}_att_{i}', font=('Any', 10), size=(400, None), auto_size_text=False)] for i in range(50)]

        self.properties = sg.Column([[self.prop_text]] + self.attributes + [[self.init_text]], size=(400, None), vertical_alignment='top')
        
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
    draw = sg.Button('Draw')

    data = get_area_data(area)
    sources = [source for source in data]

    col = [[draw, export, back]]

    fp = Properties.feature_properties
    for source in sources:
        col.append([sg.Text(source.capitalize())])

        for feature in list(data[source]):
            if fp[feature]['origin'] != source:
                continue

            color = fp[feature]['color']
            label = fp[feature]['label']

            col.append([sg.Checkbox(label, text_color = color)])
            inputs[len(inputs)] = {'type': 'checkbox', 'source': source, 'typename': feature}

    checkboxes = sg.Column(col, vertical_alignment='top')

    size = (1000,1000)

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

    drawn_types = []
    while True:
        event, values = window.read()

        print(event, values)

        if event == sg.WIN_CLOSED or event == 'Back':
            break


        if event == 'Draw':
            types = [inputs[i]['typename'] for i in inputs if values[i]]
            drawn_types = types


        if event == 'Click':
            features = []
            for source in sources:
                for typename in image_object.data[source]:
                    if typename in drawn_types:
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