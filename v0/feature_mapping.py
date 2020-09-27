import json

class csvfile:
    def __init__(self, filename, header, delimiter=','):
        self.filename = filename
        self.header = header
        self.delimiter = delimiter

        with open(filename, 'w') as f:
            f.write(delimiter.join(header) + '\n')

    def writeline(self, elements):
        line = [''] * len(self.header)

        for key, value in zip(elements.keys(), elements.values()):
            if key in self.header:
                line[self.header.index(key)] = f'"{value}"'
            
        with open(self.filename, 'a') as f:
            f.write(self.delimiter.join(line) + '\n')

if __name__ == '__main__': 
    from wfs import WFS, Feature, Filter
    from wmts import WMTS
    from gps import GPSConnection
    from maps import Map
    from utility import printe, prints, set_verbose

    typenames = []
    with open('input/filtered_categories.txt', 'r') as f:
        for line in f:
            if line[0] != '#':
                typenames.append(line[:-1])
    
    typename_dict = {
        'TL695099': 'Buildings',
        'TL965167': 'Road wells',
        'L418883_421469': 'Park trees',
        'L167365_421559': 'Park points'
    }

    markers = {
        #'downtown': (55.3947509, 10.3833619), 
        #'suburb': (55.3761308, 10.3860752), 
        #'university_parking': (55.3685818, 10.4317584), 
        #'harbor': (55.4083756, 10.3787729), 
        'park': (55.3916561, 10.3828329)
    }

    #############
    ## OPTIONS ##
    #############

    tile_matrix = 15
    r = 100
    bounding_margin = 10

    dpi = 300
    figsize = (16, 16)

    csv_header = ['feature type', 'hovedelement_tekst', 'element_tekst', 'underelement_tekst', 'fid_1', 'fid_2', 'feature #', 'lat', 'lon']

    save_everything = False

    show_figure = False
    save_figure_pdf = False
    save_figure_png = False

    save_csv = False

    areas = ['downtown']

    ####################
    ## END OF OPTIONS ##
    ####################

    width = height = 2 * (r + bounding_margin)
    
    if save_everything:
        show_figure = True
        save_figure_pdf = True
        save_figure_png = True
        save_csv = True

    try:
        if len(areas) > 0:
            markers = {key: markers[key] for key in areas}
    except:
        pass

    wfs = WFS('https://services.drift.kortinfo.net/kortinfo/services/Wfs.ashx?Site=Odense&Page=Kortopslag', 
        #username='VCSWRCSUKZ',
        #password='hrN9aTirUg5c!np',
        version='1.0.0',
        getCapabilitiesFilename='output/kortinfo_capabilities.xml'
        )
    #https://services.drift.kortinfo.net/kortinfo/services/Wmts.ashx?Site=Odense&Page=Kortopslag
    #https://services.datafordeler.dk/GeoDanmarkOrto/orto_foraar_wmts/1.0.0/WMTS?
    wmts = WMTS(use_login=True, url='https://services.datafordeler.dk/GeoDanmarkOrto/orto_foraar_wmts/1.0.0/WMTS?', 
        username='VCSWRCSUKZ',
        password='hrN9aTirUg5c!np',
        layer='orto_foraar_wmts',
        tile_matrix_set='KortforsyningTilingDK')

    for area, center in zip(markers.keys(), markers.values()):
        center = Feature(tag=area, geometry=center, srs='EPSG:4326', attributes={})
        center.to_srs('EPSG:25832')

        N = 0

        if show_figure or save_figure_pdf or save_figure_png:
            m = Map(center=center.as_srs('EPSG:25832'), wmts=wmts, figname=f'{area}', tile_matrix=tile_matrix, figsize=figsize, dpi=dpi)

        if save_csv:
            f = csvfile(f'output/{area}_features.csv', csv_header)

        filter = Filter.radius(center=center, radius=r, srs='EPSG:25832')
        bbox = Filter.bbox(center=center, width=width, height=height)

        for typename in typenames:
            if typename in typename_dict:
                typename_pretty = typename_dict[typename]
            else:
                typename_pretty = typename

            features = wfs.get_features(srs='EPSG:25832', typename=typename, bbox=bbox)

            features_inside = features.filter(lambda feature: feature.dist(center) <= r)
            features_margin = features.filter(lambda feature: r < feature.dist(center) <= r + bounding_margin)
            
            n = len(features_inside.features)

            if n > 0:
                with open(f'last_response_{typename.split(":")[-1]}.json', 'w') as jsonfile:
                    obj = features.features[0].attributes
                    json.dump(obj, jsonfile, indent=4, ensure_ascii=False)
                
                categories = []
                if save_csv:
                    features.to_srs('EPSG:4326')
                    for i, feature in enumerate(features_inside.features):
                        hovedelement_tekst = 'N/A'
                        if 'hovedelement_tekst' in feature.attributes:
                            hovedelement_tekst = feature['hovedelement_tekst']

                        element_tekst = 'N/A'
                        if 'element_tekst' in feature.attributes:
                            element_tekst = feature['element_tekst']
                            if element_tekst not in categories:
                                categories.append(element_tekst)

                        underelement_tekst = 'N/A'
                        if 'underelement_tekst' in feature.attributes:
                            underelement_tekst = feature['underelement_tekst']

                        fid = None
                        try:
                            fid = feature['fid']
                            fid1 = fid2 = fid
                            fid = fid.split('&amp;')
                            fid1, fid2 = fid
                        except:
                            fid1 = fid2 = 'N/A'

                        f.writeline({'feature type': typename_pretty, 'hovedelement_tekst': hovedelement_tekst, 'element_tekst': element_tekst, 'underelement_tekst': underelement_tekst, 'fid_1': fid1, 'fid_2': fid2, 'feature #': i + N, 'lat': feature.x(), 'lon': feature.y()})

                if show_figure or save_figure_pdf or save_figure_png:
                    m.add_feature(features_inside, label=typename_pretty, annotations=[N + i for i in range(n)])
                    m.add_feature(features_margin, label=typename_pretty, marker='x')

                N += n
            
        
        with open(f'output/{area}_features.csv', 'a') as f:    
            f.write(','.join([area, '', 'total', str(N)]) + '\n')


        if show_figure or save_figure_pdf or save_figure_png:
            m.add_circle(center, r)
            m.show(show=show_figure, save_pdf=save_figure_pdf, save_png=save_figure_png)