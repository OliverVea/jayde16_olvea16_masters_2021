from jaolma.utility.csv import CSV

import sys
import os

if len(sys.argv) > 1:
    file_paths = sys.argv[1:]

file_paths = ['D:\\WindowsFolders\\Documents\\GitHub\\jayde16_olvea16_masters_2021\\v1\\files\\area_data\\downtown_kortopslag.csv', 'D:\\WindowsFolders\\Documents\\GitHub\\jayde16_olvea16_masters_2021\\v1\\files\\area_data\\downtown_samaqua.csv', 'D:\\WindowsFolders\\Documents\\GitHub\\jayde16_olvea16_masters_2021\\v1\\files\\area_data\\downtown_geodanmark.csv']

print(file_paths)
input()

services = [file_path.split('_')[-1].split('.')[0] for file_path in file_paths]

output_name = file_paths[0].split('_')[:-1]
output_name.append(f'({",".join(services)})')
output_name = '_'.join(output_name) + '.csv'

header=['#', 'id', 'name', 'description', 'geometry']
types=['int', 'str', 'str', 'str', 'str']

output = []
n = 0
for file_path, service in zip(file_paths, services):
    csv = CSV(file_path, delimiter=',')

    content = csv.load()
    
    for i in range(len(content)):
        content[i]['#'] += n

    n += len(content)
    output.extend()

output_file = CSV.create_file(output_name, delimiter=',', header=header, content=output, types=types)