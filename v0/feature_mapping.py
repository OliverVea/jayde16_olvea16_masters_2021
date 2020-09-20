class csvfile:
    def __init__(self, filename, header, delimiter=';'):
        self.filename = filename
        self.header = header
        self.delimiter = delimiter

        with open(filename, 'w') as f:
            f.write(delimiter.join(header) + '\n')

    def writeline(self, elements):
        line = [''] * len(self.header)

        for key, value in zip(elements.keys(), elements.values()):
            if key in self.header:
                line[self.header.index(key)] = str(value)
            
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
        'TL362': 'Park points',
        'TL881260': 'Park trees'
    }

    markers = {
        #'suburb': (55.3761308, 10.3860752), 
        #'university_parking': (55.3685818, 10.4317584), 
        'downtown': (55.3947509, 10.3833619), 
        #'harbor': (55.4083756, 10.3787729), 
        #'park': (55.3916561, 10.3828329)
    }

    #############
    ## OPTIONS ##
    #############

    tile_matrix = 14
    r = 100
    width = 200
    height = 200

    dpi = 300
    figsize = (8, 8)

    csv_header = ['feature type', 'id.lokalId', 'feature #', 'lat', 'lon']

    save_everything = True

    show_figure = False
    save_figure_pdf = False
    save_figure_png = False

    save_csv = False


    ####################
    ## END OF OPTIONS ##
    ####################
    
    if save_everything:
        show_figure = True
        save_figure_pdf = True
        save_figure_png = True
        save_csv = True

    try:
        markers = {key: markers[key] for key in areas}
    except:
        pass

    wfs = WFS('https://services.drift.kortinfo.net/kortinfo/services/Wfs.ashx?Site=Odense&Page=Kortopslag', 
        #username='VCSWRCSUKZ',
        #password='hrN9aTirUg5c!np',
        #version='1.1.0'
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

            features = wfs.get_features(srs='EPSG:25832', typename=typename, bbox=bbox)
            
            n = len(features.features)

            if n > 0:

                if show_figure or save_figure_pdf or save_figure_png:
                    m.add_feature(features, label=typename_dict[features.tag], annotations=[N + i for i in range(n)])
                
                if save_csv:
                    features.to_srs('EPSG:4326')
                    for i, feature in enumerate(features.features):
                        f.writeline({'feature type': typename, 'id.lokalId': 0, 'feature #': i + N, 'lat': feature.x(), 'lon': feature.y()})

                N += n
            
        
        with open(f'output/{area}_features.csv', 'a') as f:    
            f.write(','.join([area, '', 'total', str(N)]) + '\n')


        if show_figure or save_figure_pdf or save_figure_png:
            m.add_circle(center, r)
            m.show(show=show_figure, save_pdf=save_figure_pdf, save_png=save_figure_png)

    dummy = 0