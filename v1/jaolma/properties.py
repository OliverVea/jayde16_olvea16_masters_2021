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

    default_srs = 'EPSG:25832'

    radius = 100

    feature_properties = {
        'TL695099': {'origin': 'kortopslag', 'label': 'Buildings (ki)', 'color': '#700000'},
        'TL965167': {'origin': 'kortopslag', 'label': 'Road Wells (ki)', 'color': '#ff00ff'},
        'L418883_421469': {'origin': 'kortopslag', 'label': 'Park Trees (ki)', 'color': '#00851b'},
        'L167365_421559': {'origin': 'kortopslag', 'label': 'Park Points (ki)', 'color': '#6e452f'},
        'Bygning': {'origin': 'geodanmark', 'label': 'Building (gd)', 'color': '#ff0000'},
        'Broenddaeksel': {'origin': 'geodanmark', 'label': 'Manhole Cover (gd)', 'color': '#ac0fdb'},
        'Mast': {'origin': 'geodanmark', 'label': 'Light Fixture (gd)', 'color': '#e0de38'},
        'Hegn': {'origin': 'geodanmark', 'label': 'Fence (gd)', 'color': '#cf8b5b'},
        'Soe': {'origin': 'geodanmark', 'label': 'Lake (gd)', 'color': '#3051c7'},
        'KratBevoksning': {'origin': 'geodanmark', 'label': 'Bushes (gd)', 'color': '#3b6e2f'},
        'Trae': {'origin': 'geodanmark', 'label': 'Tree (gd)', 'color': '#30c74e'},
        'Nedloebsrist': {'origin': 'geodanmark', 'label': 'Downspout Grille (gd)', 'color': '#db0f64'},
        'Chikane': {'origin': 'geodanmark', 'label': 'Chicane (gd)', 'color': '#8db09b'},
        'Vandloebskant': {'origin': 'geodanmark', 'label': 'Stream (gd)', 'color': '#6e86db'},
        'Helle': {'origin': 'geodanmark', 'label': 'Refuge Island (gd)', 'color': '#3f4f46'},
        'Skorsten': {'origin': 'geodanmark', 'label': 'Chimney (gd)', 'color': '#292927'},
        'Jernbane': {'origin': 'geodanmark', 'label': 'Railroad (gd)', 'color': '#75756a'},
        'Bassin': {'origin': 'geodanmark', 'label': 'Pool (gd)', 'color': '#00a2ff'},
        'water_node': {'origin': 'samaqua', 'label': 'Water Node (sa)', 'color': '#5b45a3'},
        'TL740798': {'origin': 'energifyn', 'label': 'Base Data (ef)', 'color': '#4a3d07'},
        'TL740800': {'origin': 'energifyn', 'label': 'Fuse Boxes (ef)', 'color': '#303030'},
        #'': {'origin': '', 'label': '', 'color': '#'},
    }

    services = {
        'wfs': {
            'energifyn': {'url': 'https://services.drift.kortinfo.net/kortinfo/services/Wfs.ashx?Site=Odense&Page=Lyssignalanlaeg', 'version': '1.0.0'},
            'kortopslag': {'url': 'https://services.drift.kortinfo.net/kortinfo/services/Wfs.ashx?Site=Odense&Page=Kortopslag', 'version': '1.0.0'},
        }
    }

    @staticmethod
    def get_feature_label(feature_name):
        if feature_name in Properties.feature_properties:
            if Properties.feature_properties[feature_name]['label'] != '':
                return Properties.feature_properties[feature_name]['label']
        return None

    @staticmethod
    def get_feature_color(feature_name):
        if feature_name in Properties.feature_properties:
            if Properties.feature_properties[feature_name]['color'] != '':
                return Properties.feature_properties[feature_name]['color']
        return None