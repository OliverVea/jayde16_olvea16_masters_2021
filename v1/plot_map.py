from jaolma.properties import Properties

import sys
import os

try:
    file_path = sys.argv[1]
except:
    path = os.path.join(os.getcwd(), 'files/areas/')

    dirs = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f)) and f in Properties.areas]

    file_path = None
    while file_path == None:
        print('\n'.join([f'{i + 1}: {dir}' for i, dir in enumerate(dirs)]))
        i = input('Please select an option or enter the full path of a .csv file: ')

        if i.isnumeric():
            i = int(i) - 1
            if 0 > i or i >= len(dirs):
                print('Invalid index.')
                continue

            dir = dirs[i]
            sub_path = os.path.join(path, dir)

            files = [f for f in os.listdir(sub_path) if os.path.isfile(os.path.join(sub_path, f)) and f.endswith('.csv')]

            if len(files) == 0:
                print(f'No .csv files in folder \'{dir}\'.')
                continue

            while True:
                print('\n'.join([f'{i + 1}: {dir}' for i, dir in enumerate(files)]))
                i = input('Please select an option: ')

                if i.isnumeric():
                    i = int(i) - 1
                    if 0 > i or i >= len(dirs):
                        print('Invalid index.')
                        continue

                    file = files[i]
                    break

            file_path = os.path.join(sub_path, file)

        else:
            print(f'Using path \'{i}\'.')
            file_path = i

with open(file_path, 'r') as f:
    print(''.join([row for row in f]))

input()