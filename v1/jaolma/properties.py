from jaolma.gis.wfs import Feature

class Properties:
    areas = {
        'downtown': (55.3947509, 10.3833619), 
        'harbor': (55.4083756, 10.3787729), 
        'park': (55.3916561, 10.3828329),
        'suburb': (55.3761308, 10.3860752), 
        'sdu': (55.3685818, 10.4317584)
    }

    # Has to only differ from areas in capitalization of letters.
    areas_pretty = ['Downtown', 'Harbor', 'Park', 'Suburb', 'SDU']

    areas = {key: Feature(geometry, 'EPSG:4326', key) for key, geometry in zip(areas.keys(), areas.values())}

    default_srs = 'EPSG:25832'

    outer_radius = 120
    radius = 100

    feature_properties = {
        'TL695099': {'origin': 'kortopslag', 'label': 'Building (ki)', 'color': '#700000'},
        'TL965167': {'origin': 'kortopslag', 'label': 'Road Well (ki)', 'color': '#ff00ff'},
        'L418883_421469': {'origin': 'kortopslag', 'label': 'Park Tree (ki)', 'color': '#00851b'},
        'L167365_421559': {'origin': 'kortopslag', 'label': 'Park Point (ki)', 'color': '#6e452f'},

        'Bygning': {'origin': 'geodanmark', 'label': 'Building (gd)', 'color': '#ff0000'},
        'Broenddaeksel': {'origin': 'geodanmark', 'label': 'Manhole Cover (gd)', 'color': '#ac0fdb'},
        'Mast': {'origin': 'geodanmark', 'label': 'Light Fixture (gd)', 'color': '#e0de38'},
        'Hegn': {'origin': 'geodanmark', 'label': 'Fence (gd)', 'color': '#cf8b5b'},
        'Soe': {'origin': 'geodanmark', 'label': 'Lake (gd)', 'color': '#3051c7'},
        'KratBevoksning': {'origin': 'geodanmark', 'label': 'Bush (gd)', 'color': '#3b6e2f'},
        'Trae': {'origin': 'geodanmark', 'label': 'Tree (gd)', 'color': '#30c74e'},
        'Nedloebsrist': {'origin': 'geodanmark', 'label': 'Downspout Grille (gd)', 'color': '#db0f64'},
        'Chikane': {'origin': 'geodanmark', 'label': 'Chicane (gd)', 'color': '#8db09b'},
        'Vandloebskant': {'origin': 'geodanmark', 'label': 'Stream (gd)', 'color': '#6e86db'},
        'Helle': {'origin': 'geodanmark', 'label': 'Refuge Island (gd)', 'color': '#3f4f46'},
        'Skorsten': {'origin': 'geodanmark', 'label': 'Chimney (gd)', 'color': '#292927'},
        'Jernbane': {'origin': 'geodanmark', 'label': 'Railroad (gd)', 'color': '#75756a'},
        'Bassin': {'origin': 'geodanmark', 'label': 'Pool (gd)', 'color': '#00a2ff'},

        'water_node': {'origin': 'samaqua', 'label': 'Water Node (sa)', 'color': '#5b45a3'},

        'TL740798': {'origin': 'energifyn', 'label': 'Base Data (ef)', 'color': '#751e1a'},
        'TL740800': {'origin': 'energifyn', 'label': 'Fuse Box (ef)', 'color': '#5e4a49'},

        'heating_cover': {'origin': 'fjernvarme', 'label': 'Heating Cover (fv)', 'color': '#47657d'},

        'Tree': {'origin': 'gnss', 'label': 'Tree (gt)', 'color': '#118a0c'},
        'Light Fixture': {'origin': 'gnss', 'label': 'Light Fixture (gt)', 'color': '#f2f55f'},
        'Downspout Grille': {'origin': 'gnss', 'label': 'Downspout Grille (gt)', 'color': '#711f80'},
        'Manhole Cover': {'origin': 'gnss', 'label': 'Manhole Cover (gt)', 'color': '#080d8a'},
        'Fuse Box': {'origin': 'gnss', 'label': 'Fuse Box (gt)', 'color': '#5c4e1c'},
        'Building Corner': {'origin': 'gnss', 'label': 'Building Corner (gt)', 'color': '#cc3618'},
        'Bench': {'origin': 'gnss', 'label': 'Bench (gt)', 'color': '#6e5942'},
        'Trash Can': {'origin': 'gnss', 'label': 'Trash Can (gt)', 'color': '#5c5b5b'},
        'Tree Stump': {'origin': 'gnss', 'label': 'Tree Stump (gt)', 'color': '#6e491b'},
        'Chimney': {'origin': 'gnss', 'label': 'Chimney (gt)', 'color': '#291937'},
        'Rock': {'origin': 'gnss', 'label': 'Rock (gt)', 'color': '#636363'},
        'Statue': {'origin': 'gnss', 'label': 'Statue (gt)', 'color': '#b3b3b3'},
        'Misc': {'origin': 'gnss', 'label': 'Misc (gt)', 'color': '#72fcfa'},

        'new_Tree': {'origin': 'gnss', 'label': 'new_Tree (gt)', 'color': '#000000'},
        'new_Light Fixture': {'origin': 'gnss', 'label': 'new_Light Fixture (gt)', 'color': '#000000'},
        'new_Downspout Grille': {'origin': 'gnss', 'label': 'new_Downspout Grille (gt)', 'color': '#000000'},
        'new_Manhole Cover': {'origin': 'gnss', 'label': 'new_Manhole Cover (gt)', 'color': '#000000'},
        'new_Fuse Box': {'origin': 'gnss', 'label': 'new_Fuse Box (gt)', 'color': '#000000'},
        'new_Building Corner': {'origin': 'gnss', 'label': 'new_Building Corner (gt)', 'color': '#000000'},
        'new_Bench': {'origin': 'gnss', 'label': 'new_Bench (gt)', 'color': '#000000'},
        'new_Trash Can': {'origin': 'gnss', 'label': 'new_Trash Can (gt)', 'color': '#000000'},
        'new_Tree Stump': {'origin': 'gnss', 'label': 'new_Tree Stump (gt)', 'color': '#000000'},
        'new_Chimney': {'origin': 'gnss', 'label': 'new_Chimney (gt)', 'color': '#000000'},
        'new_Rock': {'origin': 'gnss', 'label': 'new_Rock (gt)', 'color': '#000000'},
        'new_Statue': {'origin': 'gnss', 'label': 'new_Statue (gt)', 'color': '#000000'},
        'new_Unknown': {'origin': 'gnss', 'label': 'new_Unknown (gt)', 'color': '#000000'},
        'new_Misc': {'origin': 'gnss', 'label': 'new_Misc (gt)', 'color': '#000000'},

        'Tree_ts': {'origin': 'totalstation', 'label': 'Tree (ts)', 'color': '#118a2c'},
        'Light Fixture_ts': {'origin': 'totalstation', 'label': 'Light Fixture (ts)', 'color': '#f2f53f'},
        'Downspout Grille_ts': {'origin': 'totalstation', 'label': 'Downspout Grille (ts)', 'color': '#711f50'},
        'Manhole Cover_ts': {'origin': 'totalstation', 'label': 'Manhole Cover (ts)', 'color': '#050d8a'},
        'Building Corner_ts': {'origin': 'totalstation', 'label': 'Building Corner (ts)', 'color': '#cc3518'},
        'Bench_ts': {'origin': 'totalstation', 'label': 'Bench (ts)', 'color': '#6e5945'},
        'Trash Can_ts': {'origin': 'totalstation', 'label': 'Trash Can (ts)', 'color': '#5c5b5e'},
        'Statue_ts': {'origin': 'totalstation', 'label': 'Statue (ts)', 'color': '#b3b4b4'},
        'Greenery_ts': {'origin': 'totalstation', 'label': 'Greenery (ts)', 'color': '#128b0c'},
        'Fire Hydrant_ts': {'origin': 'totalstation', 'label': 'Fire Hydrant (ts)', 'color': '#cf4327'},
        'Misc_ts': {'origin': 'totalstation', 'label': 'Misc (ts)', 'color': '#74fcfb'},
        'unknown': {'origin': 'totalstation', 'label': 'unknown', 'color': '#000000'},
        #'': {'origin': '', 'label': '', 'color': '#'},
    }

    '''
        'Tree': {'origin': 'gnss', 'label': 'Tree (gt)', 'color': '#118a0c'},
        'Light Fixture': {'origin': 'gnss', 'label': 'Light Fixture (gt)', 'color': '#f2f55f'},
        'Downspout Grille': {'origin': 'gnss', 'label': 'Downspout Grille (gt)', 'color': '#711f80'},
        'Manhole Cover': {'origin': 'gnss', 'label': 'Manhole Cover (gt)', 'color': '#080d8a'},
        'Fuse Box': {'origin': 'gnss', 'label': 'Fuse Box (gt)', 'color': '#5c4e1c'},
        'Building Corner': {'origin': 'gnss', 'label': 'Building Corner (gt)', 'color': '#cc3618'},
        'Bench': {'origin': 'gnss', 'label': 'Bench (gt)', 'color': '#6e5942'},
        'Trash Can': {'origin': 'gnss', 'label': 'Trash Can (gt)', 'color': '#5c5b5b'},
        'Tree Stump': {'origin': 'gnss', 'label': 'Tree Stump (gt)', 'color': '#6e491b'},
        'Chimney': {'origin': 'gnss', 'label': 'Chimney (gt)', 'color': '#291937'},
        'Rock': {'origin': 'gnss', 'label': 'Rock (gt)', 'color': '#636363'},
        'Statue': {'origin': 'gnss', 'label': 'Statue (gt)', 'color': '#b3b3b3'},
        'Misc': {'origin': 'gnss', 'label': 'Misc (gt)', 'color': '#72fcfa'}
    '''
    services = {
        'wfs': {
            'geodanmark': {
                'url': 'https://services.datafordeler.dk/GeoDanmarkVektor/GeoDanmark60_NOHIST_GML3/1.0.0/WFS?', 
                'version': '1.1.0', 
                'username': 'VCSWRCSUKZ', 
                'password': 'hrN9aTirUg5c!np'},

            'energifyn': {
                'url': 'https://services.drift.kortinfo.net/kortinfo/services/Wfs.ashx?Site=Odense&Page=Lyssignalanlaeg', 
                'version': '1.0.0'},

            'kortopslag': {
                'url': 'https://services.drift.kortinfo.net/kortinfo/services/Wfs.ashx?Site=Odense&Page=Kortopslag', 
                'version': '1.0.0'},
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

    @staticmethod
    def get_feature_source(feature_name):
        if feature_name in Properties.feature_properties:
            if Properties.feature_properties[feature_name]['source'] != '':
                return Properties.feature_properties[feature_name]['source']
        return None