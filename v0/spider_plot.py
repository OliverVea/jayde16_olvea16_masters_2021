import matplotlib.pyplot as plt
import uuid
from random import random
from math import pi

class SpiderPlot:
    def __init__(self, title: str, feature_types: list, figname: str = None):
        self.N = 0
        self.category_labels = []
        self.data = []
        self.feature_types = feature_types

        self.id = figname
        if figname == None:
            self.id = uuid.uuid1()
            
        self.fig = plt.figure(self.id)

        plt.title(title)

        self.ax = plt.axes(polar=True)        
        
    def add_category(self, label, tick_values: list, tick_labels: list, color='grey', size=7):
        plt.figure(self.id)

        self.category_labels.append(label)

        self.ax.set_rlabel_position(0)
        plt.yticks(tick_values, tick_labels, color=color, size=size)
        plt.ylim(0, 1)

        self.N += 1

    def add_data(self, data, color = None):
        self.data.append((data, color))

    def show(self):
        plt.figure(self.id)
        self.angles = [n / float(self.N) * 2 * pi for n in range(self.N)]
        self.angles += self.angles[:1]

        plt.xticks(self.angles[:-1], self.category_labels, color='grey', size=8)

        self.legend_dict = {}
        for i, (data, color) in enumerate(self.data):
            #self.legend_dict[]
            lin = self.ax.plot(self.angles, data + data[:1], color=color, linewidth=1, linestyle='solid', label=self.feature_types[i])
            
            if color == None:
                color = lin[0].get_color()

            fill = self.ax.fill(self.angles, data + data[:1], 'b', color=color, alpha=0.1)

        plt.legend(bbox_to_anchor=(0.1, 0.1))

        plt.show(block=block)

if __name__ == '__main__':
    categories = ['Strength', 'Dexterity', 'Wisdom', 'Endurance', 'Luck']
    N = len(categories)
    K = 5
    d1 = [random() for _ in range(N)]
    d2 = [random() for _ in range(N)]
    d3 = [random() for _ in range(N)]

    spider_plot = SpiderPlot('title')

    for category in categories:
        spider_plot.add_category(category, [k/(K - 1) for k in range(K)], [f'{100*k/(K - 1)}%' for k in range(K)])

    colors = ['green', 'red', 'blue']
    data = [d1, d2, d3]

    for color, d in zip(colors, data):
        spider_plot.add_data(d, color)

    spider_plot.show()