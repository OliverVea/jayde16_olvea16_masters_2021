import py_compile

from os import listdir, getcwd
from os.path import isfile, join

mypath = getcwd()

onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and join(mypath, f).endswith('.py')]

for file in onlyfiles:
    py_compile.compile(file, cfile=file + 'c')