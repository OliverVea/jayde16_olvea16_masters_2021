import matplotlib.pyplot as plt
import uuid
from random import random
from math import pi

class SpiderPlot:
    def __init__(self, title: str, figname: str = None):
        self.N = 0
        self.category_labels = []
        self.data = []

        self.id = uuid.uuid1()
        self.fig = plt.figure(self.id)

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
        self.angles = [n / float(N) * 2 * pi for n in range(N)]
        self.angles += self.angles[:1]

        plt.xticks(self.angles[:-1], self.category_labels, color='grey', size=8)

        for data, color in self.data:
            self.ax.plot(self.angles, data + data[:1], color=color, linewidth=1, linestyle='solid')
            self.ax.fill(self.angles, data + data[:1], 'b', color=color, alpha=0.1)

        plt.show()

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