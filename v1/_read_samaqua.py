from jaolma.utility.csv import *

def filter(row):
    return row['X_Cover'] != 'NULL'

csv = CSV('input/Node_Cover_wHeader.csv', delimiter=',', type_row = True)
a = csv.read(filter=filter)

out = CSV('input/_Node_Cover_wHeader.csv', delimiter=',', type_row = True)
out.write(a)

pass