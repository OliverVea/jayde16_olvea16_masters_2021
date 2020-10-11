from jaolma.plotting.spider_plot import SpiderPlot

from random import random, seed

def linstring(min, max, N):
    return [n/(N - 1) * (max - min) + min for n in range(N)]

categories = ['Strength', 'Dexterity', 'Wisdom', 'Endurance', 'Luck']
N = len(categories)


seed(0)
d1 = [random() for _ in range(N)]
d2 = [random() for _ in range(N)]
d3 = [random() for _ in range(N)]

min_tick = 0.2
max_tick = 1.2
N_tick = 3

for scale_plot in [True, False][:]:
    spider_plot = SpiderPlot('title', autodraw=False, scale_plot=scale_plot, figname=f'SpiderPlot_{scale_plot}')

    for category in categories:
        tick_values = linstring(min_tick, max_tick, N_tick)
        tick_labels = [f'{100*val:0.1f}%' for val in tick_values]

        tick_values = tick_labels = None
        spider_plot.add_category(category, tick_values, tick_labels)

    colors = ['green', 'red', 'blue']
    data = [d1, d2, d3]

    for color, d in zip(colors, data):
        spider_plot.add_data(color, d, color)

    spider_plot.draw()
    spider_plot.show(show=True, block=False, save_png=True)
input()