from jaolma.gis.wfs import Feature

class Properties:
    areas = {
        'downtown': (55.3947509, 10.3833619), 
        'harbor': (55.4083756, 10.3787729), 
        'park': (55.3916561, 10.3828329),
        'suburb': (55.3761308, 10.3860752), 
        'university_parking': (55.3685818, 10.4317584)
    }

    areas = {key: Feature(geometry, 'EPSG:4326', key) for key, geometry in zip(areas.keys(), areas.values())}