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

import time

if __name__ == '__main__':
    wfs = WFS('https://services.datafordeler.dk/GeoDanmarkVektor/GeoDanmark60_NOHIST_GML3/1.0.0/WFS?', 
        username='VCSWRCSUKZ',
        password='hrN9aTirUg5c!np',
        version='1.1.0')

    for typename in ['Mast', 'Nedloebsrist', 'Skorsten', 'Telemast', 'Trae', 'Broenddaeksel']:
        collection = wfs.get_features(typename, srs='EPSG:3857', max_features=10)