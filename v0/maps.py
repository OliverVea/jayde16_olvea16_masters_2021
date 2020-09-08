from wfs import WFS, Feature, Filter
from wmts import WMTS
from utility import uniform_colors, prints, printe

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
from matplotlib.collections import PatchCollection

from time import time

class Map:
    def __init__(self, center: Feature, wmts: WMTS, figname: str = None, tile_matrix: int = 15, draw_center: bool = True):
        self.center = center
        self.srs = center.default_srs
        self.wmts = wmts
        self.figname = figname
        self.draw_center = draw_center

        self.fig = plt.figure(self.figname)

        self.set_tile_matrix(tile_matrix)
        
        plt.margins(0, 0)

        if draw_center:
            self._draw_point((0, 0), label='Center', marker='x', color=None)

    def show(self):
        plt.figure(self.figname)
        plt.show()

    def clear_points(self):
        plt.figure(self.figname)
        plt.clf()

    def set_tile_matrix(self, tile_matrix):
        self.clear_points()
        self.tile_matrix = tile_matrix
        self.background = self.wmts.get_map('default', tile_matrix=tile_matrix, center=center)
        self.dpm = self.wmts.dpm(tile_matrix)
        
        w, h = 0.5 * self.background.width / self.dpm, 0.5 * self.background.height / self.dpm
        extent = [-w, w, -h, h]

        plt.gca().set_xlim(extent[0], extent[1])
        plt.gca().set_ylim(extent[2], extent[3])

        plt.imshow(self.background, extent=extent)

    def _draw_point(self, point, label, color, marker):
        plt.plot(point[0], point[1], marker, label=label, color=color)

    def add_points(self, points: list, label: str = None, color: str = None, marker: str = '*'):
        plt.figure(self.figname)

        if not isinstance(points, list):
            points = [points]

        for point in points:
            point.to_srs(self.srs)
            self._draw_point((point - self.center).pos(), label=label, color=color, marker=marker)

    
    def add_linestrings(self, linestrings: list, label: str = None, color: str = None):
        plt.figure(self.figname)

    def add_polygons(self, polygons: list, label: str = None, color: str = None):
        plt.figure(self.figname)
        pass

    def add_circle(self, origin: Feature, radius: float):
        pass    

class MPL_Map:
    def __init__(self, coordinates: Feature, wmts: WMTS, wfs: WFS, wfs_typenames: list, wfs_colors: list = None, init_tile_matrix: int = 15, max_tile_matrix: int = 15, min_tile_matrix: int = 10, radius: float = None):
        self.coordinates = coordinates
        self.wmts = wmts
        self.wfs = wfs
        self.wfs_typenames = wfs_typenames
        self.radius = radius

        self.wfs_colors = wfs_colors
        if wfs_colors == None:
            self.wfs_colors = uniform_colors(len(wfs_typenames) + 1)

        self.tile_matrix = init_tile_matrix
        self.max_tile_matrix = max_tile_matrix
        self.min_tile_matrix = min_tile_matrix

        self.figname = f'{self.coordinates.x("EPSG:4326")}_{self.coordinates.y("EPSG:4326")}'

        self.fig = plt.figure(self.figname)
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
            type = features.type
            
            features = [ft.pos() for ft in features]

            cx, cy = self.coordinates.pos('urn:ogc:def:crs:EPSG:6.3:25832')

            if type == 'Point':
                geometry = ([x - cx for x, _ in features], [y - cy for _, y in features])

            elif type == 'Polygon':
                geometry = [[(x - cx, y - cy) for x, y in zip(xy[0], xy[1])] for xy in features]

            elif type == 'LineString':
                geometry = ([[x - cx for x in xs] for xs, _ in features], [[y - cy for y in ys] for _, ys in features])

            else:
                printe(f'Feature with type {type} not understood.', tag='MPL_Map')
                geometry = []

            self.cached_pts[(typename, filter)] = {'type': type, 'geometry': geometry}
        
        else:
            prints(f'Using cached points of type \'{typename}\'.', tag='MPL_Map')

        return self.cached_pts[(typename, filter)]

    def _update_figure(self):
        plt.clf()

        plt.title(f'Coords (lat, lon): ({self.coordinates.x("EPSG:4326")}, {self.coordinates.y("EPSG:4326")}), Tile Matrix: {self.tile_matrix}')

        dpm = self.wmts.dpm(self.tile_matrix)

        background = self.wmts.get_map(style='default', tile_matrix=self.tile_matrix, center=self.coordinates)

        r = self.radius
        if r == None:
            r = 0.5 * min(background.height, background.width) / dpm

        wfs_filter = Filter.radius(center=self.coordinates, radius=r, property='geometri')

        figpoints = []
        for typename, color in zip(self.wfs_typenames, self.wfs_colors):
            pts = self._get_points(typename, wfs_filter)

            if pts['type'] == 'Point':
                if len(pts['geometry'][0]) > 0:
                    figpoints.append(plt.plot(pts['geometry'][0], pts['geometry'][1], '*', color=color, label=typename)[0])
                
            elif pts['type'] == 'Polygon':
                patches = []
                for building in pts['geometry']:    
                    patches.append(Polygon(building))
                p = PatchCollection(patches, label=typename, facecolor='none', edgecolor=color, linewidth=2 - (0.7 / dpm))
                figpoints.append(plt.gca().add_collection(p))      
                plt.gca().add_patch(Polygon([[0,0], [0,0]], label=typename, facecolor='none', edgecolor=color))  
            
            elif pts['type'] == 'LineString':
                if len(pts['geometry'][0]) > 0:
                    xs, ys = pts['geometry']

                    for i, (x, y) in enumerate(zip(xs, ys)):
                        if i == 0:
                            figpoints.append([plt.plot(x, y, '-', color=color, label=typename)[0]])
                        else:
                            figpoints[-1].append(plt.plot(x, y, '-', color=color)[0])

        extent = [a * b / dpm for a in [background.width, background.height] for b in [-0.5, 0.5]]
        
        plt.gca().set_xlim(extent[0], extent[1])
        plt.gca().set_ylim(extent[2], extent[3])

        figpoints.append(plt.gca().add_patch(Circle((0,0), r, color=(0, 0, 0, 0.2), label='Area')))

        plt.imshow(background, extent=extent)
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

        if isinstance(pts, list):
            for pt in pts:
                pt.set_visible(not pt.get_visible())

        else:
            pts.set_visible(not pts.get_visible())
        self.fig.canvas.draw()

if __name__ == '__main__':

    from wfs import Feature

    wmts = WMTS('https://services.datafordeler.dk/GeoDanmarkOrto/orto_foraar_wmts/1.0.0/WMTS?',
        username='VCSWRCSUKZ',
        password='hrN9aTirUg5c!np',
        layer='orto_foraar_wmts',
        tile_matrix_set='KortforsyningTilingDK')

    wfs = WFS('https://services.datafordeler.dk/GeoDanmarkVektor/GeoDanmark60_NOHIST_GML3/1.0.0/WFS?', 
        username='VCSWRCSUKZ',
        password='hrN9aTirUg5c!np',
        version='1.1.0')

    typenames = ['Mast', 'Nedloebsrist', 'Skorsten', 'Telemast', 'Trae', 'Broenddaeksel', 'Bygning']

    coords = Feature('Center', geometry=(55.369837, 10.431700), srs='EPSG:4326')
    coords.to_srs('EPSG:3857')
    map = MPL_Map(coordinates=coords, wmts=wmts, wfs=wfs, wfs_typenames=typenames, init_tile_matrix=12)

if __name__ == '__main__':

    center = Feature('Center', (55.3761308,10.3860752), srs='EPSG:4326')
    center.to_srs('EPSG:3857')

    wmts = WMTS('https://services.datafordeler.dk/GeoDanmarkOrto/orto_foraar_wmts/1.0.0/WMTS?',
            username='VCSWRCSUKZ',
            password='hrN9aTirUg5c!np',
            layer='orto_foraar_wmts',
            tile_matrix_set='KortforsyningTilingDK')

    map = Map(center=center, wmts=wmts, figname='Figure', tile_matrix=13)

    d = Feature('distance', (0, 0.0001), srs='EPSG:4326')

    pts = [center + d, center - d]

    map.add_points(pts)

    map.show()