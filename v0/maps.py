<<<<<<< Updated upstream
from wfs import WFS, Feature, Filter, Point
from wmts import WMTS
=======
<<<<<<< Updated upstream
from wfs import WMTS, WFS, WFS_Feature, WFS_Filter
>>>>>>> Stashed changes
from utility import uniform_colors, prints, printe
=======
from wfs import WFS, Feature, Filter
from wmts import WMTS
from utility import uniform_colors, prints
>>>>>>> Stashed changes

import matplotlib.pyplot as plt
from matplotlib.patches import Circle

from time import time

class MPL_Map:
    def __init__(self, coordinates: Feature, wmts: WMTS, wfs: WFS, wfs_typenames: list, wfs_colors: list = None, init_tile_matrix: int = 15, max_tile_matrix: int = 15, min_tile_matrix: int = 10):
        self.coordinates = coordinates
        self.wmts = wmts
        self.wfs = wfs
        self.wfs_typenames = wfs_typenames

        self.wfs_colors = wfs_colors
        if wfs_colors == None:
            self.wfs_colors = uniform_colors(len(wfs_typenames) + 1)

        self.tile_matrix = init_tile_matrix
        self.max_tile_matrix = max_tile_matrix
        self.min_tile_matrix = min_tile_matrix

        self.fig = plt.figure()
        self.fig.canvas.mpl_connect('scroll_event', self._on_scroll)
        self.fig.canvas.mpl_connect('pick_event', self._on_pick)

        self.cached_pts = {}
        self.figpoints = {}

        self._update_figure()
        plt.show()

    def _get_points(self, typename: str, filter: str) -> tuple:
        if not (typename, filter) in self.cached_pts:
            prints(f'Requesting features of type {typename}.', tag='MPL_Map')
            features = self.wfs.get_features(typename, filter=filter, srs=self.coordinates.default_srs, as_list=True)
            features.to_srs('urn:ogc:def:crs:EPSG:6.3:25832')
            
            features = [ft.pos() for ft in features]

            cx, cy = self.coordinates.pos('urn:ogc:def:crs:EPSG:6.3:25832')

            x, y = [x - cx for x, _ in features], [y - cy for _, y in features]

            self.cached_pts[(typename, filter)] = (x, y)
        
        else:
            prints(f'Using cached points of type \'{typename}\'.', tag='MPL_Map')

        return self.cached_pts[(typename, filter)]


    def _update_figure(self):
        plt.clf()

        background = self.wmts.get_map(style='default', tile_matrix=self.tile_matrix, center=self.coordinates)

        r = 0.5 * min(background.image_height, background.image_width) / background.dpm

        wfs_filter = Filter.radius(center=self.coordinates, radius=r, property='geometri')

        figpoints = []
        for typename, color in zip(self.wfs_typenames, self.wfs_colors):
            pts = self._get_points(typename, wfs_filter)

            if len(pts[0]) > 0:
                figpoints.append(plt.plot(pts[0], pts[1], '*', color=color, label=typename)[0])

        figpoints.append(plt.gca().add_patch(Circle((0,0), r, color=(0, 0, 0, 0.2), label='Area')))

        im = background.image
        extent = [-0.5 * im.width, 0.5 * im.width, -0.5 * im.height, 0.5 * im.height]
        extent = [e / background.dpm for e in extent]

        plt.imshow(im, extent=extent)
        plt.margins(0, 0)

        legend = plt.legend()
        
        self.figpoints = {}
        for legend_entry, pts in zip(legend.get_lines(), figpoints):
            legend_entry.set_picker(True)
            legend_entry.set_pickradius(8)
            self.figpoints[legend_entry] = pts

        plt.draw()
        prints('Map has been drawn.', tag='MPL_Map')
        

    def _on_scroll(self, event):
        if event.button == 'up' and self.tile_matrix < self.max_tile_matrix:
            self.tile_matrix += 1
        elif event.button == 'down' and self.tile_matrix > self.min_tile_matrix:
            self.tile_matrix -= 1
            
        prints(f'Scrolled {event.button}. tile_matrix now {self.tile_matrix}.', tag='MPL_Map')
        self._update_figure()

    def _on_pick(self, event):
        pts = self.figpoints[event.artist]
        pts.set_visible(not pts.get_visible())
        self.fig.canvas.draw()

if __name__ == '__main__':

    from wfs import Point

    wmts = WMTS('https://services.datafordeler.dk/GeoDanmarkOrto/orto_foraar_wmts/1.0.0/WMTS?',
        username='VCSWRCSUKZ',
        password='hrN9aTirUg5c!np',
        layer='orto_foraar_wmts',
        tile_matrix_set='KortforsyningTilingDK')

    wfs = WFS('https://services.datafordeler.dk/GeoDanmarkVektor/GeoDanmark60_NOHIST_GML3/1.0.0/WFS?', 
        username='VCSWRCSUKZ',
        password='hrN9aTirUg5c!np',
        version='1.1.0')

    typenames = ['Mast', 'Nedloebsrist', 'Skorsten', 'Telemast', 'Trae', 'Broenddaeksel']

    coords = Point(geometry=(55.369837, 10.431700), default_srs='EPSG:4326')
    coords.to_srs('EPSG:3857')
    map = MPL_Map(coordinates=coords, wmts=wmts, wfs=wfs, wfs_typenames=typenames, init_tile_matrix=10)