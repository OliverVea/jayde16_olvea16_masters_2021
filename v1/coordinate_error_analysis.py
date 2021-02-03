from jaolma.plotting.spider_plot import spider_plot
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

from jaolma.data_treatment.data_treatment import GISData
from jaolma.properties import Properties


gis_data = [GISData(area, use_exclude_property=True) for area in Properties.areas]
stats = [g.get_stats() for g in gis_data]

error_by_source = {}
for source in GISData.all_sources:
    error_by_source[source] = {}

    source_stats = [stat[source] for stat in stats]
    typenames = set([typename for stat in source_stats for typename in stat])
    typenames = [typename for typename in typenames if not Properties.feature_properties[typename]['exclude']]

    for typename in typenames:
        error = 0
        n = 0
        for s in source_stats:
            if not typename in s or s[typename] == None:
                continue
            
            acc = s[typename].get_accuracy()

            if np.isnan(acc):
                continue

            error += acc * len(s[typename].true_positives)
            n += len(s[typename].true_positives)
        
        error_by_source[source][typename] = error / n

with open('error_by_source.csv', 'w') as f:
    for source in error_by_source:
        for typename in error_by_source[source]:
            f.write(f'{source},{typename},{error_by_source[source][typename]}\n')
