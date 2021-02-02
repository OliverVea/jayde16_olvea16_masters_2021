from jaolma.plotting.spider_plot import spider_plot
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

from jaolma.gather_data import GISData
from jaolma.properties import Properties


gis_data = [GISData(area) for area in Properties.areas]
stats = [g.get_stats() for g in gis_data]

def get_precision(stats, source, area):
    stats = stats[source]
    stats = [stat for stat in stats.values() if stat != None]

    if len(stats) == 0:
        print(f'Could not find precision for source {source} in area {area}, as there were no features. Returning nan.')
        return np.nan

    tps = sum([len(stat.true_positives) for stat in stats])
    fps = sum([len(stat.false_positives) for stat in stats])
    return tps / (tps + fps)

def get_recall(stats, source, area):
    stats = stats[source]
    stats = [stat for stat in stats.values() if stat != None]

    if len(stats) == 0:
        print(f'Could not find recall for source {source} in area {area}, as there were no features. Returning nan.')
        return np.nan

    tps = sum([len(stat.true_positives) for stat in stats])
    fns = sum([len(stat.false_negatives) for stat in stats])

    if tps + fns == 0:
        print(f'Could not find recall for source {source} in area {area}, as there were no features. Returning nan.')
        return np.nan

    return tps / (tps + fns)

def get_f1(stats, source, area):
    recall = get_recall(stats, source, area)
    precision = get_precision(stats, source, area)

    if recall == 0 or precision == 0:
        return 0

    return 2 / (1/recall + 1/precision)

def get_accuracy(stats, source, area):
    stats = stats[source]
    stats = [stat for stat in stats.values() if stat != None]

    if len(stats) == 0:
        print(f'Could not find accuracy for source {source} in area {area}, as there were no features. Returning nan.')
        return np.nan

    tps = [len(stat.true_positives) for stat in stats]
    accuracies = [stat.get_accuracy() for stat in stats]

    s = sum([tp*acc for tp, acc in zip(tps, accuracies)])
    n = sum(tps)

    return s / n

def get_accessibility(stats, source, area):
    stats = stats[source]
    stats = [stat for stat in stats.values() if stat != None]

    if len(stats) == 0:
        print(f'Could not find accuracy for source {source} in area {area}, as there were no features. Returning nan.')
        return np.nan
    
    tps = [len(stat.true_positives) for stat in stats]
    accuracies = [stat.get_accessibility() for stat in stats]

    s = sum(tp*acc for tp, acc in zip(tps, accuracies) if not np.isnan(acc))
    n = sum(tp for tp, acc in zip(tps, accuracies) if not np.isnan(acc))

    if n == 0:
        return np.nan

    return s / n

def get_visibility(stats, source, area):
    stats = stats[source]
    stats = [stat for stat in stats.values() if stat != None]

    if len(stats) == 0:
        print(f'Could not find accuracy for source {source} in area {area}, as there were no features. Returning nan.')
        return np.nan
    
    tps = [len(stat.true_positives) for stat in stats]
    accuracies = [stat.get_visibility() for stat in stats]

    s = sum(tp*acc for tp, acc in zip(tps, accuracies) if not np.isnan(acc))
    n = sum(tp for tp, acc in zip(tps, accuracies) if not np.isnan(acc))

    if n == 0:
        return np.nan

    return s / n

labels = ['Precision', 'Recall', 'F1']

if True:
    for stat, fn in zip(['Precision', 'Recall', 'F1'], [get_precision, get_recall, get_f1]):
        silhouettes = {source: [fn(d, source, area) for area, d in zip(Properties.areas_pretty, stats)] for source in GISData.all_sources}

        fig = spider_plot(
            f'Area {stat}',
            labels=Properties.areas_pretty,
            silhouettes=silhouettes,
            axis_value_labels=False,
            axis_value_decimals=2,
            scale_type='set',
            axis_max=[1 for _ in Properties.areas_pretty],
            axis_min=[0 for _ in Properties.areas_pretty],
            marker='o',
            marker_size=3,
        )

        plt.savefig(f'sp_{stat}.pdf')
        plt.show(block=False)

if True:
    silhouettes = {source: [get_accuracy(d, source, area) for area, d in zip(Properties.areas_pretty, stats)] for source in GISData.all_sources}
    
    fig = spider_plot(
        f'Area Error',
        labels=Properties.areas_pretty,
        silhouettes=silhouettes,
        axis_value_labels=False,
        axis_value_decimals=2,
        reversed_axes=[True for _ in Properties.areas_pretty],
        marker='o',
        marker_size=3,
    )

    plt.savefig(f'sp_Error.pdf')
    plt.show(block=False)

if True:
    silhouettes = {source: [get_accessibility(d, source, area) for area, d in zip(Properties.areas_pretty, stats)] for source in GISData.all_sources}
    
    fig = spider_plot(
        f'Area Accessibility',
        labels=Properties.areas_pretty,
        silhouettes=silhouettes,
        axis_value_labels=False,
        axis_value_decimals=2,
        marker='o',
        marker_size=3,
    )

    plt.savefig(f'sp_Acc.pdf')
    plt.show(block=False)

if True:
    silhouettes = {source: [get_visibility(d, source, area) for area, d in zip(Properties.areas_pretty, stats)] for source in GISData.all_sources}
    
    fig = spider_plot(
        f'Area Visibility',
        labels=Properties.areas_pretty,
        silhouettes=silhouettes,
        axis_value_labels=False,
        axis_value_decimals=2,
        marker='o',
        marker_size=3,
    )

    plt.savefig(f'sp_Vis.pdf')
    plt.show(block=True)


