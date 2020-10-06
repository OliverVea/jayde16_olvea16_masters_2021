from lxml import objectify
from jaolma.gis.wfs import WFS, Filter

capabilities = ['kortinfo', 'energifyn', 'geodanmark']


def read_capabilities(sourcename):
    with open(f'files/capabilities_{sourcename}.xml', 'r') as f:
        content = objectify.fromstring(f.read())   
    return content

capabilities = {sourcename: read_capabilities(sourcename) for sourcename in capabilities}

def get_types(content, clean=False):

    el = content.find('.//{http://www.opengis.net/wfs}FeatureTypeList')

    types = [str(child.Name) for child in el.getchildren()]

    if clean:
        types = [type.split(' ')[-1] for type in types]
        types = [type.split(':')[-1] for type in types]

    return types

types = {sourcename: get_types(content, clean=True) for sourcename, content in zip(capabilities.keys(), capabilities.values())}

print('sourcename n_types')
for sourcename, content, type in zip(capabilities.keys(), capabilities.values(), types.values()):
    print(sourcename, len(type))
print()

common = [type for type in types['kortinfo'] if type in types['energifyn']]
print('kortinfo and energifyn overlap:', len(common))