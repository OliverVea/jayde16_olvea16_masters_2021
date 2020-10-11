from jaolma.plotting.spider_plot import SpiderPlot

from random import random, seed

categories = ['Strength', 'Dexterity', 'Wisdom', 'Endurance', 'Luck']
N = len(categories)
K = 5
seed(0)
d1 = [random() for _ in range(N)]
d2 = [random() for _ in range(N)]
d3 = [random() for _ in range(N)]

spider_plot = SpiderPlot('title', autodraw=False, scale_plot=False)

for category in categories:
    spider_plot.add_category(category, [k/(K-1) for k in range(K)], [f'{100*k/(K-1)}%' for k in range(K)])

colors = ['green', 'red', 'blue']
data = [d1, d2, d3]

for color, d in zip(colors, data):
    spider_plot.add_data(color, d, color)

spider_plot.draw()
spider_plot.show()