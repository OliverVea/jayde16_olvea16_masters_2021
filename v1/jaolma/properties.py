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

    feature_properties = {
        'TL695099': {'label': 'Buildings (ki)', 'color': '#700000'},
        'TL965167': {'label': 'Road Wells (ki)', 'color': '#ff00ff'},
        'L418883_421469': {'label': 'Park Trees (ki)', 'color': '#00851b'},
        'L167365_421559': {'label': 'Park Points (ki)', 'color': '#6e452f'},
        'Bygning': {'label': 'Building (gd)', 'color': '#ff0000'},
        'Broenddaeksel': {'label': 'Manhole Cover (gd)', 'color': '#ac0fdb'},
        'Mast': {'label': 'Light Fixture (gd)', 'color': '#e0de38'},
        'Hegn': {'label': 'Fence (gd)', 'color': '#cf8b5b'},
        'Soe': {'label': 'Lake (gd)', 'color': '#3051c7'},
        'KratBevoksning': {'label': 'Bushes (gd)', 'color': '#3b6e2f'},
        'Trae': {'label': 'Tree (gd)', 'color': '#30c74e'},
        'Nedloebsrist': {'label': 'Downspout Grille (gd)', 'color': '#db0f64'},
        'Chikane': {'label': 'Chicane (gd)', 'color': '#8db09b'},
        'Vandloebskant': {'label': 'Stream (gd)', 'color': '#6e86db'},
        'Helle': {'label': 'Refuge Island (gd)', 'color': '#3f4f46'},
        'Skorsten': {'label': 'Chimney (gd)', 'color': '#292927'},
        'Jernbane': {'label': 'Railroad (gd)', 'color': '#75756a'},
        'Bassin': {'label': 'Pool (gd)', 'color': '#00a2ff'},
    }

    @staticmethod
    def get_feature_label(feature_name):
        if feature_name in Properties.feature_properties:
            if Properties.feature_properties[feature_name]['label'] != '':
                return Properties.feature_properties[feature_name]['label']
        return ''

    @staticmethod
    def get_feature_color(feature_name):
        if feature_name in Properties.feature_properties:
            if Properties.feature_properties[feature_name]['color'] != '':
                return Properties.feature_properties[feature_name]['color']
        return None