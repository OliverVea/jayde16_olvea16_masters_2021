from utility import printe, prints

from requests import get, post
from lxml import objectify
import json

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

    def get_features(self, typename=None, bbox=None, filter=None, max_features=None, srs_name=None):
        url = self._make_url(request='GetFeature', typename=typename, bbox=bbox, filter=filter, maxFeatures=max_features, srsName=srs_name)
        featureCollection = self._query_url(url)

        if featureCollection == None:
            return {}

        assert(self._simplify_tag(featureCollection.tag) == 'FeatureCollection')

        mastlist = [member.getchildren()[0] for member in featureCollection.iterchildren()]
        mastdict = {}

        for mast in mastlist:
            mastdictentry = {}
            for attribute in mast.iterchildren():
                tag = self._simplify_tag(attribute.tag)

                if tag == 'geometri':
                    mastdictentry[tag] = self._get_geometry(attribute)

                else:
                    mastdictentry[tag] = attribute.text

            assert(not mastdictentry['id.lokalId'] in mastdict)
            mastdict[mastdictentry['id.lokalId']] = mastdictentry

        return mastdict

    def _query_url(self, url):
        response = post(url)
        content = response.content
        content = objectify.fromstring(content)

        children = {self._simplify_tag(c.tag): c for c in content.iterchildren()}

        if 'Exception' in children:
            printe(children['Exception'].ExceptionText)
            return None

        return content

wfs = WFS('https://services.datafordeler.dk/GeoDanmarkVektor/GeoDanmark60_NOHIST_GML3/1.0.0/WFS?', 
    username='VCSWRCSUKZ',
    password='hrN9aTirUg5c!np',
    version='1.1.0')

url = wfs._make_url(request='GetFeature', typename='Mast', maxFeatures=5)

# EPSG:3857 - WGS 84 / Pseudo-Mercator
# EPSG:4326 - WGS 84

masts = wfs.get_features(typename='Mast', max_features=5, srs_name='EPSG:3857')

prints(f'Exported {len(masts)} features.')

with open('data.json', 'w') as f:
    json.dump(masts, f, indent=4)