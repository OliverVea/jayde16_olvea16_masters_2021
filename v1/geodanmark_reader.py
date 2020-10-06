from lxml import objectify
from jaolma.gis.wfs import WFS, Filter

capabilities = ['kortopslag', 'energifyn', 'geodanmark']


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
        types = [type.capitalize() for type in types]

    return types

def get_titles(content, clean=False):
    el = content.find('.//{http://www.opengis.net/wfs}FeatureTypeList')

    titles = [str(child.Title) for child in el.getchildren()]

    if clean:
        titles = [type.lower() for type in titles]
        titles = [type.replace(' ', '_') for type in titles]
        titles = [type.replace('(', '') for type in titles]
        titles = [type.replace(')', '') for type in titles]
        titles = [type.replace(',', '') for type in titles]
        titles = [type.replace('.', '') for type in titles]

        danish_letters = {'ø': 'o', 'oe': 'o', 'å': 'a', 'aa': 'a', 'æ': 'e', 'ae': 'e'}
        for danish_letter in danish_letters:
            titles = [title.replace(danish_letter, danish_letters[danish_letter]) for title in titles]

    return titles

types = {sourcename: get_titles(content, clean=True) for sourcename, content in zip(capabilities.keys(), capabilities.values())}

print('sourcename n_types')
for sourcename, content, type in zip(capabilities.keys(), capabilities.values(), types.values()):
    print(sourcename, len(type))
print()

common = [type for type in types['kortinfo'] if type in types['energifyn']]
print('kortinfo and energifyn overlap:', len(common))
print(f'kortinfo procent: {100*len(common)/len(types["kortinfo"]):.2f}%')
print(f'energifyn procent: {100*len(common)/len(types["energifyn"]):.2f}%')