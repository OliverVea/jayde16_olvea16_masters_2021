from jaolma.plotting.spider_plot import spider_plot
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

from jaolma.data_treatment.data_treatment import GISData
from jaolma.properties import Properties


gis_data = [GISData(area, use_exclude_property=True) for area in Properties.areas]
stats = [g.get_stats() for g in gis_data]

plots = {'overview': False, 'perf': False, 'err': False, 'acc': False, 'vis': False, 'n': True, 'n_all': False}

def get_gt_count(data):
    features = []
    for fts in data.ground_truth.values():
        features.extend(fts)

    return len(features)

def get_count(stats, source, area, false_positives: bool = False):
    stats = stats[source]
    stats = [stat for stat in stats.values() if stat != None]

    if len(stats) == 0:
        print(f'Could not find precision for source {source} in area {area}, as there were no features. Returning 0.')
        return 0

    tps = [len(stat.true_positives) for stat in stats]
    s = sum(tp for tp in tps if not np.isnan(tp))

    if false_positives:
        fps = [len(stat.false_positives) for stat in stats]
        s += sum(fp for fp in fps if not np.isnan(fp))

    return s

def get_precision(stats, source, area):
    stats = stats[source]
    stats = [stat for stat in stats.values() if stat != None]

    if len(stats) == 0:
        print(f'Could not find precision for source {source} in area {area}, as there were no features. Returning nan.')
        return np.nan

    tps = sum([len(stat.true_positives) for stat in stats])
    fps = sum([len(stat.false_positives) for stat in stats])
    return tps / (tps + fps) * 100

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

    return tps / (tps + fns) * 100

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

if plots['overview']:
    labels = ['Amount', 'Precision', 'Recall', 'Visibility', 'Accessibility', 'Error']

    silhouettes = {}
    data = stats

    for source in GISData.all_sources:
        silhouettes[source] = [0 for _ in labels]

        silhouettes[source][0] = sum(get_count(d, source, area) for area, d in zip(Properties.areas_pretty, stats))

        # Precision
        s = [len(stats.true_positives) for d in data for stats in d[source].values() if stats != None]
        n = [len(stats.true_positives) + len(stats.false_positives) for d in data for stats in d[source].values() if stats != None]
        silhouettes[source][1] = sum(s) / sum(n) * 100

        # Recall
        s = [len(stats.true_positives) for d in data for stats in d[source].values() if stats != None]
        n = [len(stats.true_positives) + len(stats.false_negatives) for d in data for stats in d[source].values() if stats != None]
        silhouettes[source][2] = sum(s) / sum(n) * 100

        # Visibility
        s = [stats.get_visibility() * len(stats.true_positives) for d in data for stats in d[source].values() if stats != None and not np.isnan(stats.get_visibility())]
        n = [len(stats.true_positives) for d in data for stats in d[source].values() if stats != None and not np.isnan(stats.get_visibility())]
        silhouettes[source][3] = sum(s) / sum(n)

        # Accessibility
        s = [stats.get_accessibility() * len(stats.true_positives) for d in data for stats in d[source].values() if stats != None and not np.isnan(stats.get_accessibility())]
        n = [len(stats.true_positives) for d in data for stats in d[source].values() if stats != None and not np.isnan(stats.get_accessibility())]
        silhouettes[source][4] = sum(s) / sum(n)

        # Accuracy
        s = [stats.get_accuracy() * len(stats.true_positives) for d in data for stats in d[source].values() if stats != None and not np.isnan(stats.get_accuracy())]
        n = [len(stats.true_positives) for d in data for stats in d[source].values() if stats != None and not np.isnan(stats.get_accuracy())]
        silhouettes[source][5] = sum(s) / sum(n)

    axis_max = [max(silhouettes[source][0] for source in GISData.all_sources), 100, 100, 100, 100, max(silhouettes[source][5] for source in GISData.all_sources)]


    silhouettes = {Properties.source_labels[source]: silhouettes[source] for i, source in enumerate(silhouettes)}
    fig = spider_plot(
        f'Source Overview',
        labels=labels,
        silhouettes=silhouettes,
        axis_value_labels=False,
        axis_value_decimals=2,
        marker='o',
        marker_size=3,
        reversed_axes=[label == 'Error' for label in labels],
        scale_type='set',
        axis_min=[0 for _ in labels],
        axis_max=axis_max,
        silhouette_line_color=[Properties.source_colors[source] for source in GISData.all_sources],
        #legend_loc='right',
        legend_bbox=(0.75, 0.05),
    )

    plt.savefig(f'sp_Overview.pdf')

labels = ['Precision', 'Recall', 'F1']
if plots['perf']:
    for stat, fn in zip(labels, [get_precision, get_recall, get_f1]):
        silhouettes = {source: [fn(d, source, area) for area, d in zip(Properties.areas_pretty, stats)] for source in GISData.all_sources}

        silhouettes = {Properties.source_labels[source]: silhouettes[source] for i, source in enumerate(silhouettes)}
        fig = spider_plot(
            f'Area {stat}',
            labels=Properties.areas_pretty,
            silhouettes=silhouettes,
            axis_value_labels=False,
            axis_value_decimals=2,
            scale_type='set',
            axis_max=[100 for _ in Properties.areas_pretty],
            axis_min=[0 for _ in Properties.areas_pretty],
            marker='o',
            marker_size=3,
            legend_loc=None,
            legend_bbox=None,
            silhouette_line_color=[Properties.source_colors[source] for source in GISData.all_sources],
        )

        plt.savefig(f'sp_{stat}.pdf')

if plots['err']:
    silhouettes = {source: [get_accuracy(d, source, area) for area, d in zip(Properties.areas_pretty, stats)] for source in GISData.all_sources}
    
    silhouettes = {Properties.source_labels[source]: silhouettes[source] for i, source in enumerate(silhouettes)}
    fig = spider_plot(
        f'Area Error [m]',
        labels=Properties.areas_pretty,
        silhouettes=silhouettes,
        axis_value_labels=False,
        axis_value_decimals=2,
        reversed_axes=[True for _ in Properties.areas_pretty],
        marker='o',
        marker_size=3,
        legend_loc=None,
        legend_bbox=None,
        silhouette_line_color=[Properties.source_colors[source] for source in GISData.all_sources],
    )

    plt.savefig(f'sp_Error.pdf')

if plots['acc']:
    silhouettes = {source: [get_accessibility(d, source, area) for area, d in zip(Properties.areas_pretty, stats)] for source in GISData.all_sources}
    
    silhouettes = {Properties.source_labels[source]: silhouettes[source] for i, source in enumerate(silhouettes)}
    fig = spider_plot(
        f'Area Accessibility',
        labels=Properties.areas_pretty,
        silhouettes=silhouettes,
        axis_value_labels=False,
        axis_value_decimals=2,
        marker='o',
        marker_size=3,
        legend_loc=None,
        legend_bbox=None,
        silhouette_line_color=[Properties.source_colors[source] for source in GISData.all_sources],
    )

    plt.savefig(f'sp_Acc.pdf')

if plots['vis']:
    silhouettes = {source: [get_visibility(d, source, area) for area, d in zip(Properties.areas_pretty, stats)] for source in GISData.all_sources}
    
    silhouettes = {Properties.source_labels[source]: silhouettes[source] for i, source in enumerate(silhouettes)}
    fig = spider_plot(
        f'Area Visibility',
        labels=Properties.areas_pretty,
        silhouettes=silhouettes,
        axis_value_labels=False,
        axis_value_decimals=2,
        marker='o',
        marker_size=3,
        legend_loc=None,
        legend_bbox=None,
        silhouette_line_color=[Properties.source_colors[source] for source in GISData.all_sources],
    )

    plt.savefig(f'sp_Vis.pdf')

if plots['n']:
    silhouettes = {source: [get_count(d, source, area) for area, d in zip(Properties.areas_pretty, stats)] for source in GISData.all_sources}
    #silhouettes.update({'groundtruth': [get_gt_count(d) for d in gis_data]})
    sources = [source for source in silhouettes]

    silhouettes = {Properties.source_labels[source]: silhouettes[source] for i, source in enumerate(silhouettes)}
    fig = spider_plot(
        f'Area Feature Count (True Positives)',
        labels=Properties.areas_pretty,
        silhouettes=silhouettes,
        axis_value_labels=False,
        axis_value_decimals=0,
        marker='o',
        marker_size=3,
        legend_loc=None,
        legend_bbox=None,
        silhouette_line_color=[Properties.source_colors[source] for source in sources],
    )

    plt.savefig(f'sp_N_TP.pdf')

if plots['n_all']:
    silhouettes = {source: [get_count(d, source, area, false_positives=True) for area, d in zip(Properties.areas_pretty, stats)] for source in GISData.all_sources}
    silhouettes.update({'groundtruth': [get_gt_count(d) for d in gis_data]})
    
    silhouettes = {Properties.source_labels[source]: silhouettes[source] for i, source in enumerate(silhouettes)}
    fig = spider_plot(
        f'Area Feature Count (True Positives and False Positives)',
        labels=Properties.areas_pretty,
        silhouettes=silhouettes,
        axis_value_labels=False,
        axis_value_decimals=0,
        marker='o',
        marker_size=3,
        legend_loc=None,
        legend_bbox=None,
        silhouette_line_color=[Properties.source_colors[source] for source in GISData.all_sources],
    )

    plt.savefig(f'sp_N_All.pdf')


plt.show()