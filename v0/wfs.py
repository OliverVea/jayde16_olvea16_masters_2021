from utility import printe, prints, shortstring

import io

from requests import get, post
from lxml import objectify, etree
from pyproj import Transformer
from PIL import Image
    
class Feature(object):
    def __init__(self, tag, attributes = {}):
    
        self.tag = tag
        self.attributes = attributes

    def __getitem__(self, key):
        return self.attributes[key]

    def __setitem__(self, key, value):
        self.attributes[key] = value

class Point(Feature):
    def __init__(self, geometry: tuple, srs: str, attributes = {}):
        super().__init__('Point', attributes)

        self.default_srs = srs
        
        self.points = {srs: geometry}

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

class Polygon(Feature):
    def __init__(self, geometry: list, srs: str, attributes = {}):
        super().__init__('Polygon', attributes)

        self.default_srs = srs
        
        self.points = {srs: geometry}
    
    def __iter__(self):
        return self.points[self.default_srs].__iter__()

    def pos(self, srs=None, transform: callable = None):
        if srs == None:
            return self.points[self.default_srs]

        if not srs in self.points:
            if transform == None:
                transformer = Transformer.from_crs(self.default_srs, srs)
                self.points[srs] = transformer.transform(self.xs(), self.ys())

            else:
                self.points[srs] = transform(self.xs(), self.ys())

        return self.points[srs]

    
    def xs(self, srs=None):
        return self.pos(srs)[0]

    def ys(self, srs=None):
        return self.pos(srs)[1]

    def to_srs(self, srs, transform: callable = None):
        self.points[srs] = self.pos(srs, transform)
        self.default_srs = srs

class LineString(Polygon):
    def __init__(self, geometry: list, srs: str, attributes = {}):
        Feature.__init__(self, 'LineString', attributes)

        self.default_srs = srs
        
        self.points = {srs: geometry}

# Måske: 
# Feature ┬─> Point
#         └─> Polygon
# i stedet for:     
# Point ─> Feature (ifht. inheritance)
# 
# x()/y() giver ikke super meget mening og geometry skal ændres for Polygon alligevel. Collection har features som kan være en af polymorpherne af Feature.
# Det giver også meget god mening at Point er et WFS point og ikke bare en primitive som man måske kunne tro nu.


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
    def __init__(self, tag: str, type: str, features: list, srs: str):
        self.tag = tag
        self.type = type
        self.features = features
        self.cached_srs = [srs]

    def __iter__(self):
        return self.features.__iter__()

    def to_srs(self, srs):
        if len(self.features) > 0 and srs not in self.cached_srs:
            transformer = Transformer.from_crs(self.cached_srs[0], srs)

            for ft in self.features:
                ft.to_srs(srs, transformer.transform)

            self.cached_srs.append(srs)

        else:
            for ft in self.features:
                ft.to_srs(srs)


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
                with open('last_response.xml', 'wb') as f:
                    f.write(etree.tostring(content, pretty_print=True))
                return content
        except:
            pass

        if response_type == 'jpeg':
            return Image.open(io.BytesIO(content))


class WFS(WebService):
    def _get_geometry(self, element):

        element = element.getchildren()[0]
        tag = self._simplify_tag(element.tag)

        if tag == 'Point':
            element = element.getchildren()[0]
            assert(self._simplify_tag(element.tag) == 'pos')
            geometry = tuple(float(val) for val in element.text.split(' '))

        elif tag == 'Polygon':
            t = './/{http://www.opengis.net/gml/3.2}posList'
            temp_geometry = [float(val) for val in element.find(t).text.split(' ')]
            geometry = [tuple(temp_geometry[i*3+j] for i in range(len(temp_geometry)//3)) for j in range(3)]

        elif tag == 'LineString':
            t = './/{http://www.opengis.net/gml/3.2}posList'
            temp_geometry = [float(val) for val in element.find(t).text.split(' ')]
            geometry = [tuple(temp_geometry[i*3+j] for i in range(len(temp_geometry)//3)) for j in range(3)]

        else:
            printe(f'Geometry type {tag} not supported.', tag='WFS._get_geometry')
            geometry = []
            
        return geometry, tag


    def get_features(self, srs, typename=None, bbox=None, filter=None, max_features=None, as_list=False):
        url = self._make_url('wfs', request='GetFeature', typename=typename, bbox=bbox, filter=filter, maxFeatures=max_features, srsName=srs)
        featureCollection = self._query_url(url)

        if featureCollection == None or self._simplify_tag(featureCollection.tag) != 'FeatureCollection':
            printe('Error in retrieving features. Returning empty dictionary.', tag='WFS')
            return {}

        featurelist = [member.getchildren()[0] for member in featureCollection.iterchildren()]
        features = []

        type = "None"

        for ft in featurelist:
            attributes = {}
            for attribute in ft.iterchildren():
                tag = self._simplify_tag(attribute.tag)

                if tag == 'geometri':
                    geometry, type = self._get_geometry(attribute)

                else:
                    attributes[tag] = attribute.text

            if type == 'Point':
                featureType = Point
            elif type == 'Polygon':
                featureType = Polygon
            elif type == 'LineString':
                featureType = LineString
            else:
                printe(f'Geometry type {type} not supported.', tag='WFS.get_features')
                featureType = Point
                geometry = (0, 0)

            feature = featureType(geometry=geometry, srs=srs, attributes=attributes)
            features.append(feature)

        features = Collection(type=type, tag=str(typename), features=features, srs=srs)

        prints(f'Received {len(featurelist)} features from \'{shortstring(url, maxlen=90)}\'.', tag='WFS')

        return features

if __name__ == '__main__':
    wfs = WFS('https://services.datafordeler.dk/GeoDanmarkVektor/GeoDanmark60_NOHIST_GML3/1.0.0/WFS?', 
        username='VCSWRCSUKZ',
        password='hrN9aTirUg5c!np',
        version='1.1.0')

    for typename in ['Mast', 'Bygning']:
        collection = wfs.get_features(typename=typename, srs='EPSG:3857', max_features=3)

    collection.to_srs('EPSG:4326')
    dummy = 0