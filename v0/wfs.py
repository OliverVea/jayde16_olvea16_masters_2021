from utility import printe, prints, set_verbose, shortstring

from requests import get, post
from lxml import objectify
import json
from pyproj import Transformer

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

class WFS:
    def __init__(self, url, username, password, version):
        self.url = url
        self.username = username
        self.password = password
        self.version = version

    def _make_url(self, use_login=True, **args):
        arguments = {'service': 'wfs', 'version': self.version}
        arguments.update(args)

        if use_login:
            arguments['username'] = self.username
            arguments['password'] = self.password

        arguments = [f'{str(key)}={str(value)}' for key, value in zip(arguments.keys(), arguments.values()) if value != None]
        arguments = '&'.join(arguments)

        return self.url + arguments

    def _simplify_tag(self, tag):
        return tag.split('}')[-1]

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
        url = self._make_url(request='GetFeature', typename=typename, bbox=bbox, filter=filter, maxFeatures=max_features, srsName=srs_name)
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

    def _query_url(self, url):
        response = get(url)
        content = response.content
        content = objectify.fromstring(content)

        children = {self._simplify_tag(c.tag): c for c in content.iterchildren()}

        if 'Exception' in children:
            printe(str(children['Exception'].ExceptionText), 'wfs')
            return None

        return content


wfs = WFS('https://services.datafordeler.dk/GeoDanmarkVektor/GeoDanmark60_NOHIST_GML3/1.0.0/WFS?', 
    username='VCSWRCSUKZ',
    password='hrN9aTirUg5c!np',
    version='1.1.0')

wfs_filter = open('filter.xml', 'r').read()

for ch in ['\t', '\n']:
    wfs_filter = wfs_filter.replace(ch, '')

#wfs_filter = None

# EPSG:3857 - WGS 84 / Pseudo-Mercator
# EPSG:4326 - WGS 84

typenames = ['Mast', 'Nedloebsrist', 'Skorsten', 'Telemast', 'Trae', 'Broenddaeksel']
colors = ['#FF0000', '#0000FF', '#FFFF00', '#FF00FF', '#00FF00', 'grey']

gmap3 = gmplot.GoogleMapPlotter(55.3685394, 10.4288793, 16, apikey='AIzaSyA0y2iofkkWlv8v5KnAYpkW8KBRopsN8Ag')

for typename, color in zip(typenames, colors):
    prints(f'Requesting features of type {typename}.')
    features = wfs.get_features(typename=typename, srs_name='EPSG:3857', max_features=None, filter=wfs_filter)

    prints('Transforming points...')
    pts = [feature.pos('EPSG:4326') for feature in features.values()]
    pts_lat, pts_lon = [pt[0] for pt in pts], [pt[1] for pt in pts]

    prints('Plotting points.')
    gmap3.scatter(pts_lat, pts_lon,size=30, color=color)

gmap3.draw('map.html')

prints('Map has been drawn.')