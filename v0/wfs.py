from utility import printe, prints, shortstring

import io

from requests import get, post
from lxml import objectify, etree
from pyproj import Transformer
from PIL import Image
    
class Point(object):
    def __init__(self, geometry: tuple, default_srs: str):
        self.default_srs = default_srs
        
        self.points = {default_srs: geometry}

    def __iter__(self):
        return self.points[self.default_srs].__iter__()

    def pos(self, srs=None, transform: callable = None):
        if srs == None:
            srs = self.default_srs

        if not srs in self.points:
            if transform == None:
                transformer = Transformer.from_crs(self.default_srs, srs)
                self.points[srs] = transformer.transform(self.x(), self.y())

            else:
                self.points[srs] = transform(self.x(), self.y())

        return self.points[srs]

    def x(self, srs=None):
        return self.pos(srs)[0]

    def y(self, srs=None):
        return self.pos(srs)[1]

    def to_srs(self, srs, transform: callable = None):
        self.points[srs] = self.pos(srs, transform)
        self.default_srs = srs

class Feature(Point):
    def __init__(self, tag, geometry, default_srs, attributes = {}):
        super(Feature, self).__init__(geometry, default_srs)
    
        self.tag = tag
        self.attributes = attributes

    def __getitem__(self, key):
        return self.attributes[key]

    def __setitem__(self, key, value):
        self.attributes[key] = value

class Filter:
    @staticmethod
    def radius(center: Feature, radius: float, property: str = 'geometri', srs: str = None):
        with open('filter_templates/radius.xml', 'r') as f:
            filt = f.read()

        for ch in ['\t', '\n']:
            filt = filt.replace(ch, '')

        filt = filt.replace('rrr', str(radius))
        filt = filt.replace('ppp', property)

        if srs != None:
            filt = filt.replace('xxx', str(center.x(srs=srs)))
            filt = filt.replace('yyy', str(center.y(srs=srs)))
            filt = filt.replace('ccc', srs)

        else:
            filt = filt.replace('xxx', str(center.x()))
            filt = filt.replace('yyy', str(center.y()))
            filt = filt.replace('ccc', center.default_srs)

        return filt

class Collection:
    def __init__(self, tag: str, features: list):
        self.tag = tag
        self.features = features

    def __iter__(self):
        return self.features.__iter__()

    def to_srs(self, srs):
        transformer = None
        if len(self.features) > 0 and not srs in self.features[0].points:
            transformer = Transformer.from_crs(self.features[0].default_srs, srs)

        for ft in self.features:
            ft.to_srs(srs, transformer.transform)

class WebService(object):
    def __init__(self, url, username, password, version):
        self.url = url
        self.username = username
        self.password = password
        self.version = version

    def _make_url(self, service, use_login=True, **args):
        arguments = {'service': service, 'version': self.version}
        arguments.update(args)

        if use_login:
            arguments['username'] = self.username
            arguments['password'] = self.password

        arguments = [f'{str(key)}={str(value)}' for key, value in zip(arguments.keys(), arguments.values()) if value != None]
        arguments = '&'.join(arguments)

        return self.url + arguments

    def _simplify_tag(self, tag):
        return tag.split('}')[-1]

    def _query_url(self, url, response_type='xml'):
        response = get(url)
        content = response.content

        try:
            content = objectify.fromstring(content)

            children = {self._simplify_tag(c.tag): c for c in content.iterchildren()}

            if 'Exception' in children:
                printe(str(children['Exception'].ExceptionText), tag='WebService')
                return None

            if response_type == 'xml':
                return content
        except:
            pass
        
        if response_type == 'jpeg':
            return Image.open(io.BytesIO(content))


class WFS(WebService):
    def _get_geometry(self, element):
        tag = self._simplify_tag(element.tag)

        if tag == 'Point':
            element = element.getchildren()[0]
            assert(self._simplify_tag(element.tag) == 'pos')
            return tuple(float(val) for val in element.text.split(' '))
        
        geometry = [self._get_geometry(c) for c in element.iterchildren()]
        if len(geometry) == 1:
            geometry = geometry[0]

        return geometry

    def get_features(self, typename=None, bbox=None, filter=None, max_features=None, srs=None, as_list=False):
        url = self._make_url('wfs', request='GetFeature', typename=typename, bbox=bbox, filter=filter, maxFeatures=max_features, srsName=srs)
        featureCollection = self._query_url(url)

        if featureCollection == None or self._simplify_tag(featureCollection.tag) != 'FeatureCollection':
            printe('Error in retrieving features. Returning empty dictionary.', tag='WFS')
            return {}

        featurelist = [member.getchildren()[0] for member in featureCollection.iterchildren()]
        features = []

        for feature in featurelist:
            attributes = {}
            for attribute in feature.iterchildren():
                tag = self._simplify_tag(attribute.tag)

                if tag == 'geometri':
                    geometry = self._get_geometry(attribute)

                else:
                    attributes[tag] = attribute.text

            feature = Feature(tag=self._simplify_tag(feature.tag), geometry=geometry, default_srs=srs, attributes=attributes)
            features.append(feature)

        features = Collection(tag=str(typename), features=features)

        prints(f'Received {len(featurelist)} features from \'{shortstring(url, maxlen=90)}\'.', tag='WFS')

        return features

<<<<<<< Updated upstream
import time
=======
<<<<<<< Updated upstream
class WMTS(WebService):
    def __init__(self, url: str, username: str, password: str, layer: str, tile_matrix_set: str, format: str='image/jpeg', version: str='1.0.0'):
        super(WMTS, self).__init__(url, username, password, version)
        self.pixel_size = 0.00028
        self.layer = layer
        self.format = format
        self.tile_matrix_set = tile_matrix_set

        self.cache = {}

        self._get_capabilities()


    def _to_px(self, scale_denominator, rw=None, m=None):
        if rw != None:
            return rw / (self.pixel_size * scale_denominator)
        return m / self.pixel_size

    def _to_rw(self, scale_denominator, px=None, m=None):
        if px != None:
            return px * self.pixel_size * scale_denominator
        return m * scale_denominator

    def _to_map(self, scale_denominator, px=None, rw=None):
        if px != None:
            return px * self.pixel_size
        return rw / scale_denominator

    def _get_capabilities(self):
        url = self._make_url(service='wmts', request='GetCapabilities')
        response = self._query_url(url)

        tms = response.Contents.TileMatrixSet

        t = './/{http://www.opengis.net/ows/1.1}SupportedCRS'
        self.crs = str(tms.find(t).text)

        def to_obj(tile_matrix):
            tlc = tile_matrix.TopLeftCorner.text.split(' ')

            tm = {
                'matrix_height':        int(tile_matrix.MatrixHeight),
                'matrix_width':         int(tile_matrix.MatrixWidth),
                'scale_denominator':    float(tile_matrix.ScaleDenominator),
                'tile_height':          int(tile_matrix.TileHeight),
                'tile_width':           int(tile_matrix.TileWidth),
                'top_left_x':           float(tlc[0]),
                'top_left_y':           float(tlc[1]),
            }

            
            tm['map_width'] = self._to_rw(tm['scale_denominator'], px=tm['tile_width'] * tm['matrix_width'])
            tm['map_height'] = self._to_rw(tm['scale_denominator'], px=tm['tile_height'] * tm['matrix_height'])

            return tm

        self.tile_matrices = [to_obj(c) for c in tms.iterchildren() if self._simplify_tag(c.tag) == 'TileMatrix']

    def _get_tile(self, style, tile_matrix, row, col):
        key = (style, tile_matrix, row, col)

        if key in self.cache:
            return self.cache[key]

        url = self._make_url(service='wmts', request='GetTile', layer=self.layer, style=style, format=self.format, tilematrixset=self.tile_matrix_set, tilematrix=tile_matrix, tileRow=row, tileCol=col)
        response = self._query_url(url, response_type='jpeg')
=======
>>>>>>> Stashed changes

        self.cache[key] = response

        return response

    def _stitch_images(self, images, rows, cols, image_width, image_height):
        width = len(images) * image_width
        height = len(images[0]) * image_height
        parent_img = Image.new('RGB', (width, height))

        for col, imgs in enumerate(images):
            for row, im in enumerate(imgs):
                parent_img.paste(im, (col * image_width, row * image_height))

        return parent_img

    def get_map(self, style: str, tile_matrix: int, center: WFS_Feature, screen_width: int = 1920, screen_height: int = 1080):
        tm = self.tile_matrices[tile_matrix]

        cols = ceil((screen_width/2) / tm['tile_width'])
        rows = ceil((screen_height/2) / tm['tile_height'])

        x = center.x(srs=self.crs)
        center_x = tm['matrix_width'] * (x - tm['top_left_x']) / tm['map_width']
        center_col = int(center_x)

        y = center.y(srs=self.crs)
        center_y = tm['matrix_height'] * (tm['top_left_y'] - y) / tm['map_height']
        center_row = int(center_y)

        tiles = []
        for col in range(center_col - cols, cols + center_col + 1):
            if col >= 0:
                tile_col = []        
                for row in range(center_row - rows, rows + center_row + 1):
                    if row >= 0:
                        tile = self._get_tile(style, tile_matrix, row=row, col=col)
                        tile_col.append(tile)
                tiles.append(tile_col)

        m = self._stitch_images(tiles, rows*2+1, cols*2+1, tm['tile_width'], tm['tile_height'])

        tx = (cols + center_x - center_col) * tm['tile_width']
        ty = (rows + center_y - center_row) * tm['tile_height']


        crop = (
            int(tx-screen_width/2), 
            int(ty-screen_height/2), 
            int(tx+screen_width/2), 
            int(ty+screen_height/2))

        m = m.crop(crop)

        return self.WMTS_Map(center, m, 1 / (self.pixel_size * tm['scale_denominator']))

    class WMTS_Map:
        def __init__(self, center: WFS_Feature, image: Image.Image, dpm: float):
            self.center = center
            self.image = image
            self.dpm = dpm

            self.image_width = image.width
            self.image_height = image.height
>>>>>>> Stashed changes

if __name__ == '__main__':
    wfs = WFS('https://services.datafordeler.dk/GeoDanmarkVektor/GeoDanmark60_NOHIST_GML3/1.0.0/WFS?', 
        username='VCSWRCSUKZ',
        password='hrN9aTirUg5c!np',
        version='1.1.0')

    for typename in ['Mast', 'Nedloebsrist', 'Skorsten', 'Telemast', 'Trae', 'Broenddaeksel']:
        collection = wfs.get_features(typename, srs='EPSG:3857', max_features=10)