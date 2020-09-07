from wfs import WFS, Feature, Filter
from wmts import WMTS
from utility import uniform_colors, prints

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
from matplotlib.collections import PatchCollection

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

        self.entries_visible = []

        self.cached_pts = {}
        self.figpoints = {}

        self._update_figure()
        plt.show()

    def _get_points(self, typename: str, filter: str) -> tuple:
        if not (typename, filter) in self.cached_pts:
            prints(f'Requesting features of type {typename}.', tag='MPL_Map')
            features = self.wfs.get_features(typename=typename, filter=filter, srs=self.coordinates.default_srs, as_list=True)
            features.to_srs('urn:ogc:def:crs:EPSG:6.3:25832')
            
            features = [ft.pos() for ft in features]

            cx, cy = self.coordinates.pos('urn:ogc:def:crs:EPSG:6.3:25832')

            x, y = [x - cx for x, _ in features], [y - cy for _, y in features]

            self.cached_pts[(typename, filter)] = (x, y)
        
        else:
            prints(f'Using cached points of type \'{typename}\'.', tag='MPL_Map')

        return self.cached_pts[(typename, filter)]

    def _get_building_points(self, filter: str) -> tuple:
        if not ('Bygning', filter) in self.cached_pts:
            prints('Requesting features of type Bygning.', tag='MPL_Map')
            buildings = self.wfs.get_features(typename='Bygning', filter=filter, srs=self.coordinates.default_srs, as_list=True)
            buildings.to_srs('urn:ogc:def:crs:EPSG:6.3:25832')
            
            buildings = [points.pos() for points in buildings]

            cx, cy = self.coordinates.pos('urn:ogc:def:crs:EPSG:6.3:25832')

            center = [cx, cy]

            #image_poses = [[[x - cx for x in building[0]], [y - cy for y in building[1]]] for building in buildings]
            #for i in range(len(image_poses)): image_poses[i] = list(zip(*image_poses[i]))

            image_poses = [[[xy - c for xy, c in zip([x, y], center)] for x, y in zip(xy[0], xy[1])] for xy in buildings]

            self.cached_pts[('Bygning', filter)] = image_poses
        
        else:
            prints('Using cached points of type Bygning.', tag='MPL_Map')

        return self.cached_pts[('Bygning', filter)]

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

        #Add buildings     
        building_pts = self._get_building_points(wfs_filter)
        patches = []
        for building in building_pts:    
            patches.append(Polygon(building))
        p = PatchCollection(patches, label='Buildings', facecolor='none', edgecolor='red', linewidth=2 - (0.7 / background.dpm))
        figpoints.append(plt.gca().add_collection(p))
        plt.gca().set_xlim(- 0.5 * background.image_width / background.dpm, 0.5 * background.image_width / background.dpm)
        plt.gca().set_ylim(- 0.5 * background.image_height / background.dpm, 0.5 * background.image_height / background.dpm)
        

        #matplotlib can't add PatchCollection to legend, this is used to fix it.
        plt.gca().add_patch(Polygon([[0,0], [0,0]], label='Buildings', facecolor='none', edgecolor='red'))

        figpoints.append(plt.gca().add_patch(Circle((0,0), r, color=(0, 0, 0, 0.2), label='Area')))

        im = background.image
        extent = [-0.5 * im.width, 0.5 * im.width, -0.5 * im.height, 0.5 * im.height]
        extent = [e / background.dpm for e in extent]

        plt.imshow(im, extent=extent)
        plt.margins(0, 0)

        legend = plt.legend()

        legend_entries = legend.get_lines() + legend.get_patches()

        for legend_entry, pts in zip(legend_entries, figpoints):
            legend_entry.set_picker(8)

            entry_label = legend_entry.get_label()
            if entry_label in self.figpoints:
                visible = self.figpoints[entry_label].get_visible()
                pts.set_visible(visible)

            self.figpoints[entry_label] = pts

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
        pts = self.figpoints[event.artist.get_label()]
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

    coords = Point(geometry=(55.369837, 10.431700), srs='EPSG:4326')
    coords.to_srs('EPSG:3857')
    map = MPL_Map(coordinates=coords, wmts=wmts, wfs=wfs, wfs_typenames=typenames, init_tile_matrix=12)