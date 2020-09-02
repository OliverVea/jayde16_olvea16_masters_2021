from utility import printe, prints, set_verbose, shortstring

from requests import get, post
from lxml import objectify
import json
from pyproj import Proj, transform

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
        if self._simplify_tag(element.tag) == 'pos':
            return list(float(val) for val in element.text.split(' '))

        if element.text != None:
            return element.text
        
        return {self._simplify_tag(c.tag): self._get_geometry(c) for c in element.iterchildren()}

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
            featureentry = {}
            for attribute in feature.iterchildren():
                tag = self._simplify_tag(attribute.tag)

                if tag == 'geometri':
                    featureentry[tag] = self._get_geometry(attribute)

                else:
                    featureentry[tag] = attribute.text

            if as_list:
                features.append(featureentry)
            else:
                assert(not featureentry['id.lokalId'] in features)
                features[featureentry['id.lokalId']] = featureentry

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

    #Returns the position of a point from one srs in another srs
    def transform_point(self, x, y, input_srs='epsg:3857', output_srs='epsg:4326'):
        input_proj = Proj(init=input_srs)
        output_proj = Proj(init=output_srs)
        return transform(input_proj, output_proj, x, y)


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

masts = wfs.get_features(typename='Mast', srs_name='EPSG:3857', as_list=True, max_features=None, filter=wfs_filter)

point = masts[0]['geometri']['Point']['pos']

point_4326 = wfs.transform_point(point[0], point[1])

with open('data.json', 'w') as f:
    json.dump(masts, f, indent=4)