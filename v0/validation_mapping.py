from wfs import WFS, Collection, Feature, Filter
from wmts import WMTS
from gps import GPSConnection
from maps import Map
from utility import printe, prints, set_verbose

from read_csv import CSV

#############
## OPTIONS ##
#############

tile_matrix = 15
r = 100

dpi = 300
figsize = (14, 14)

show_figure = True
save_figure_pdf = True
save_figure_png = True

area = 'downtown'

####################
## END OF OPTIONS ##
####################

csv = CSV(f'input/{area}.csv')
features = csv.read()

true_positives = Collection(tag='True Positives', type='Various', features=[feature for feature in features if feature['Category'] == 'True Positive'], srs='EPSG:4326')
false_positives = Collection(tag='False Positives', type='Various', features=[feature for feature in features if feature['Category'] == 'False Positive'], srs='EPSG:4326')
false_negatives = Collection(tag='False Negatives', type='Various', features=[feature for feature in features if feature['Category'] == 'False Negative'], srs='EPSG:4326')
unknown = Collection(tag='Unknown', type='Various', features=[feature for feature in features if feature['Category'] == 'Unknown'], srs='EPSG:4326')

markers = {
    'suburbs': (55.3761308, 10.3860752), 
    'university_parking': (55.3685818, 10.4317584), 
    'downtown': (55.3947509, 10.3833619), 
    'harbor': (55.4083756, 10.3787729), 
    'park': (55.3916561, 10.3828329)
    }

wmts = WMTS('https://services.datafordeler.dk/GeoDanmarkOrto/orto_foraar_wmts/1.0.0/WMTS?',
    username='VCSWRCSUKZ',
    password='hrN9aTirUg5c!np',
    layer='orto_foraar_wmts',
    tile_matrix_set='KortforsyningTilingDK')

center = Feature(tag=area, geometry=markers[area], srs='EPSG:4326', attributes={})
center.to_srs('EPSG:3857')

N = 0

m = Map(center=center.as_srs('urn:ogc:def:crs:EPSG:6.3:25832'), wmts=wmts, figname=f'{area}', tile_matrix=tile_matrix, figsize=figsize, dpi=dpi)

filter = Filter.radius(center=center, radius=r)

markers = ['o', 'x', 's', '*']

tag_dict = {
    'Point': ['Broenddaeksel', 'Mast', 'Nedloebsrist', 'Trae', 'Skorsten'],
    'LineString': ['Hegn', 'Chikane', 'Vandloebskant', 'Helle', 'Trafikhegn', 'Jernbane'],
    'Polygon': ['Bygning', 'KratBevoksning', 'Soe', 'Bassin']
}

for collection, marker in zip([true_positives, false_positives, false_negatives, unknown], markers):
    for type, tags in zip(tag_dict.keys(), tag_dict.values()):
        if type == 'LineString' or type == 'Polygon':
            if marker == 'o':
                marker = '-'

            elif marker == 'x':
                marker = '--'

            elif marker == 's':
                marker = ':'

            elif marker == '*':
                marker = '-.'

        for tag in tags:
            features = collection.filter(lambda feature: feature['Feature Tag'] == tag)
            features.type = type
            features.tag = tag

            annotations = [feature['Feature #'] for feature in features]
            m.add_feature(features, label=features.tag, annotations=annotations, marker=marker)

if show_figure or save_figure_pdf or save_figure_png:
    m.add_circle(center, r)
    m.show(show=show_figure, save_pdf=save_figure_pdf, save_png=save_figure_png)
