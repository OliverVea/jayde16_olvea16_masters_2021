from jaolma.properties import Properties
from jaolma.utility.utility import transpose, Color, printe, prints
from jaolma.gis.wfs import Feature
from jaolma.gis.wmts import WMTS
from jaolma.gui.properties_box import PropertiesBox

from PIL import Image, ImageDraw

import PySimpleGUI as sg
import pandas as pd

import os

class Plot_Image:
    class Layer:
        def __init__(self, features: list, typename: str, size: tuple, cache: bool = True, r: float = 2, fill = None, outline = None, text_color = None):
            self.cache = cache
            self.typename = typename

            self.layer = Image.new('RGBA', size)
            draw = ImageDraw.Draw(self.layer)

            self.is_gnss = typename in [typename for typename in Properties.feature_properties if Properties.feature_properties[typename]['origin'] == 'gnss']

            if self.is_gnss:
                r *= 1.5


            if fill == None: 
                fill = Properties.feature_properties[typename]['color']

            if outline == None:
                outline = Color(fill) * 0.75
                

            for ft in features:
                x, y = ft['plot_x'], ft['plot_y']
                xy = [(x - r, y - r), (x + r, y + r)]

                draw.ellipse(xy=xy, fill=fill, outline=outline)

                if self.is_gnss:
                    draw.text(xy=[x + r, y + r], text=f'{ft["id"]}')

            if not cache:
                self.layer.save(f'files/gui/layers/{typename}.png')
                self.layer.close()

        def __enter__(self):
            if not self.cache:
                self.layer = Image.open(f'files/gui/layers/{self.typename}.png')
            return self.layer

        def __exit__(self, type, value, traceback):
            if not self.cache:
                self.layer.close()

    def __init__(self, size: tuple, area: str, data: dict, tile_matrix: int = 14, background_path: str = 'files/gui/background.png', image_path: str = 'files/gui/image.png', r: float = 3, cache: bool = True):
        self.wmts = WMTS(
            use_login=True,
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

        self.r = r
        self.cache = cache

        self.data = {}
        self.layers = {}

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

                self.layers[typename] = self.Layer(features, typename, self.background.size, self.cache)

    def get_image(self, show_circle: bool = True, show_annotations: bool = True, r: float = 3):
        with Image.open(self.backgound_path) as im:
            draw = ImageDraw.Draw(im)

            for typename in self.data['gnss']:
                for feature in self.data['gnss'][typename]:
                    for source in [source for source in self.data if source != 'gnss']:
                        if pd.notna(feature[source]):
                            id = feature[source]
                            for typename in self.data[source]:
                                for ft in self.data[source][typename]:
                                    if ft['id'] == id:
                                        draw.line([(ft['plot_x'], ft['plot_y']), (feature['plot_x'], feature['plot_y'])], fill='black')

            for typename in self.layers:
                with self.layers[typename] as layer:
                    im.paste(layer, (0,0), layer)

            if show_circle:
                x0 = (self.size[0] / 2 - Properties.radius * self.dpm, self.size[1] / 2 - Properties.radius * self.dpm)
                x1 = (self.size[0] / 2 + Properties.radius * self.dpm, self.size[1] / 2 + Properties.radius * self.dpm)

                draw.ellipse([x0, x1], outline='#ff0000')

            im.save(self.image_path)

        return self.image_path

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

    size = (2001,2001)

    image_object = Plot_Image(size=size, area=area, data=data)

    graph = sg.Graph(canvas_size=size, graph_bottom_left=(0,0), graph_top_right=size, key='Click', enable_events=True)

    layout = [[graph]]

    window = sg.Window(title, layout)
    window.finalize()

    graph.DrawImage(image_object.get_image([]), location=(0, size[1]))

    while True:
        event, _ = window.read()

        if event == sg.WIN_CLOSED or event == 'Back':
            break

        if event == 'Click':
            pass    

        graph.DrawImage(image_object.get_image(), location=(0, size[1]))

    window.close()

    return event

if __name__ == '__main__':
    sg.theme('DarkGrey2')
    plot('suburb')