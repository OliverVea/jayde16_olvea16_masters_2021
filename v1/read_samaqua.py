from jaolma.utility.csv import *
from jaolma.properties import Properties
from math import sqrt

radius = 100

for area in Properties.areas:

    center = Properties.areas[area].as_srs(srs='EPSG:25832').points['EPSG:25832']

    def filter(row):
        if row['X_Node'] != None:
            return sqrt((row['X_Node'] - center[0])**2 + (row['Y_Node'] - center[1])**2) < radius
        return False

    #header_node_cover = CSV('input/Samaqua/HeaderNodeCover.csv', delimiter=';').load()
    node_type_code = CSV('input/Samaqua/NodeTypeCode.csv', delimiter=';')
    d_knudekode_beskrivelse = {row['KnudeKode']: row['Beskrivelse'] for row in node_type_code.load()}

    origin_code = CSV('input/Samaqua/OriginCode.csv', delimiter=';')
    d_coordorigincode_beskrivelse = {row['CoordOriginCode']: row['Beskrivelse'] for row in origin_code.load()}

    owner_id = CSV('input/Samaqua/OwnerID_wHeader.csv', delimiter=';')
    d_oid_ownershipname = {row['ObjectID']: row[' OwnershipName'] for row in owner_id.load()}
    
    origin_journal = CSV('input/Samaqua/OriginJournal_wHeader.csv', delimiter=';')
    d_oid_journal = {row['ObjectID']: row for row in origin_journal.load()}

    nodes = CSV('input/Samaqua/Node_Cover_wHeader.csv', delimiter=';').load()

    for row in nodes:
        update = {}
        object_id = row['OID_Node']
        update['Ownership'] = d_oid_ownershipname.setdefault(object_id, 'None')

        if object_id in d_oid_journal:
            journal = d_oid_journal[object_id]
        else:
            journal = {key: None for key in origin_journal.get_header()}

        a = list(d_oid_journal.keys())[960:970]

        row.setdefault('KnudeKode', 'None')
        update['KnudeBeskrivelse'] = objectid_ownershipname.setdefault(row['KnudeKode'], 'None')

        if any([val != 'None' for val in [update['Ownership'], update['KnudeBeskrivelse']]]):
            print(update)

        origin_journal[i].update(update)


    pass
    for i, row in enumerate(input_data):
        if row['FeatureGUID'] not in [data['id'] for data in output_data]:
            output_data.append({})
            output_data[i]['#'] = i
            output_data[i]['id'] = row['FeatureGUID']
            output_data[i]['name'] = 'water_node'
            output_data[i]['description'] = 'Water node'
            output_data[i]['geometry'] = f'"Point;{row["X_Node"]},{row["Y_Node"]}"'

    if len(output_data) > 0:
        types = [type(typ).__name__ for typ in output_data[0].values()]
        CSV.create_file('files/area_data/' + area + '_samaqua.csv', delimiter=',', header=output_data[0].keys(), content=output_data, types=types)