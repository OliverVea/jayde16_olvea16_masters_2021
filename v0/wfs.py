from utility import printe, prints, set_verbose, shortstring

from requests import get, post
from lxml import objectify, etree

import json
from pyproj import Transformer

from PIL import Image

import binascii

import gmplot

class WFS_Feature:
    def __init__(self, tag, attributes, geometry, default_srs):
        self.tag = tag
        self.attributes = attributes
        self.geometry = geometry
        self.default_srs = default_srs

        self.transformed_points = {}

    def __getitem__(self, key):
        return self.attributes[key]

    def __setitem__(self, key, value):
        self.attributes[key] = value

    def __iter__(self):
        return self.geometry.__iter__()

    def pos(self, srs=None):
        if srs != None:
            if not srs in self.transformed_points:
                transformer = Transformer.from_crs(self.default_srs, srs)
                self.transformed_points[srs] = transformer.transform(self.geometry[0], self.geometry[1])
            return self.transformed_points[srs]
        return self.geometry

    def x(self, srs=None):
        return self.pos(srs)[0]

    def y(self, srs=None):
        return self.pos(srs)[1]

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
                printe(str(children['Exception'].ExceptionText), 'wfs')
                return None

            if response_type == 'xml':
                return content
        except:
            pass
        
        if response_type == 'jpeg':
            with open('template_image.jpeg', 'wb') as f:
                f.write(content)
            return Image.open('template_image.jpeg')


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

    def get_features(self, typename=None, bbox=None, filter=None, max_features=None, srs_name=None, as_list=False):
        url = self._make_url('wfs', request='GetFeature', typename=typename, bbox=bbox, filter=filter, maxFeatures=max_features, srsName=srs_name)
        featureCollection = self._query_url(url)

        if featureCollection == None or self._simplify_tag(featureCollection.tag) != 'FeatureCollection':
            printe('Error in retrieving features. Returning empty dictionary.', 'wfs')
            return {}

        featurelist = [member.getchildren()[0] for member in featureCollection.iterchildren()]
        features = {}
        if as_list:
            features = []

        for feature in featurelist:
            attributes = {}
            for attribute in feature.iterchildren():
                tag = self._simplify_tag(attribute.tag)

                if tag == 'geometri':
                    geometry = self._get_geometry(attribute)

                else:
                    attributes[tag] = attribute.text

            feature = WFS_Feature(self._simplify_tag(feature.tag), attributes, geometry, srs_name)

            if as_list:
                features.append(feature)
            else:
                assert(not feature['id.lokalId'] in features)
                features[feature['id.lokalId']] = feature

        prints(f'Received {len(featurelist)} features from \'{shortstring(url, maxlen=100)}\'.', tag='wfs')

        return features

class WMTS(WebService):
    def __init__(self, url: str, username: str, password: str, layer: str, tile_matrix_set: str, format: str='image/jpeg', version: str='1.0.0'):
        super(WMTS, self).__init__(url, username, password, version)
        self.layer = layer
        self.format = format
        self.tile_matrix_set = tile_matrix_set

        self.cache = {}

        self._get_capabilities()


    def _to_px(self, scale_denominator, rw=None, m=None):
        if rw != None:
            return rw / (0.00028 * scale_denominator)
        return m / 0.00028

    def _to_rw(self, scale_denominator, px=None, m=None):
        if px != None:
            return px * 0.00028 * scale_denominator
        return m * scale_denominator

    def _to_map(self, scale_denominator, px=None, rw=None):
        if px != None:
            return px * 0.00028
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

        self.cache[key] = response

        return response

    def get_map(self, style: str, tile_matrix: int, center: WFS_Feature, screen_width: int = 1920, screen_height: int = 1080):
        tm = self.tile_matrices[tile_matrix]

        x = center.x(srs=self.crs)
        dx = x - tm['top_left_x']
        tx = dx / tm['map_width']
        tile_x = tx * tm['matrix_width']
        col = int(tile_x)

        y = center.y(srs=self.crs)
        dy = tm['top_left_y'] - y
        ty = dy / tm['map_height']
        tile_y = ty * tm['matrix_height']
        row = int(tile_y)

        tile = self._get_tile(style, tile_matrix, row=row, col=col)
        tile.show()