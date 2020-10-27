import matplotlib.pyplot as plt
import uuid
from random import random
from math import pi
from jaolma.plotting.spider_plot import SpiderPlot
from jaolma.utility.read_csv import CSV
from jaolma.properties import Properties
from jaolma.utility.utility import uniform_colors, linspace, transpose

def _invert(x, limits):
    """inverts a value x on a scale from
    limits[0] to limits[1]"""
    return limits[1] - (x - limits[0])

def _scale_data(data, ranges):
    """scales data[1:] to ranges[0],
    inverts if the scale is reversed"""
    # for d, (y1, y2) in zip(data[1:], ranges[1:]):
    for d, (y1, y2) in zip(data, ranges):
        assert (y1 <= d <= y2) or (y2 <= d <= y1)

    x1, x2 = ranges[0]
    d = data[0]

    if x1 > x2:
        d = _invert(d, (x1, x2))
        x1, x2 = x2, x1

    sdata = [d]

    for d, (y1, y2) in zip(data[1:], ranges[1:]):
        if y1 > y2:
            d = _invert(d, (y1, y2))
            y1, y2 = y2, y1

        sdata.append((d-y1) / (y2-y1) * (x2 - x1) + x1)

    return sdata

def plot(self, data, *args, **kw):
    sdata = _scale_data(data, self.ranges)
    self.ax.plot(self.angle, np.r_[sdata, sdata[0]], *args, **kw)
def fill(self, data, *args, **kw):
    sdata = _scale_data(data, self.ranges)
    self.ax.fill(self.angle, np.r_[sdata, sdata[0]], *args, **kw)


categories = Properties.feature_properties

areas = ['Harbor', 'Park', 'SDU', 'Suburb']

N = len(areas)
K = len(categories)

spider_plot = SpiderPlot(title='Features Across Areas', figname='Features Across Areas', autodraw=False, scale_plot=False, figsize=(12,12))

colors = uniform_colors(N)

all_data = []

for area in areas:

    csv_file = CSV(f'input/SpiderData/{area}_Data_Analysis.csv')
    features = csv_file.read()

    for cat in categories:
        categories[cat]['amount'] = 0

    for cat in categories:
        for ft in features:
            if ft['Feature Tag'] == cat:
                categories[cat]['amount'] += 1

    data_list = []
    for cat in categories:
        data_list.append(categories[cat]['amount'])

    #data_list = [d/max(data_list) for d in data_list]
    
    all_data.append(data_list)



for i, category in enumerate(categories):
    min_tick = 0
    max_tick = max(transpose(all_data)[i])
    N_tick = 5

    tick_values = linspace(min_tick, max_tick, N_tick)
    tick_labels = tick_values

    spider_plot.add_category(Properties.get_feature_label(category), tick_values, tick_labels)


for area, color, d in zip(areas, colors, all_data):
    spider_plot.add_data(area, d, color=color)

spider_plot.draw()
spider_plot.show(save_png=False)