import matplotlib.pyplot as plt
import uuid
from random import random
from math import pi

class SpiderPlot:
    class Shape:
        def __init__(self, line=None, fill=None, legline=None):
            self.line = line
            self.fill = fill
            self.legline = legline
            self.set_state('transparent')

        def set_line(self, line):
            self.line = line

        def set_fill(self, fill):
            self.fill = fill

        def set_legline(self, legline, pick_radius):
            self.legline = legline
            self.legline.set_picker(True)
            self.legline.set_pickradius(pick_radius)
        
        def set_state(self, state: str = None):
            if None not in [self.line, self.fill, self.legline]:
                if state == 'visible':
                    self.line.set_alpha(0.8)
                    self.fill.set_alpha(0.8)
                    self.legline.set_alpha(0.8)
                elif state == 'transparent':
                    self.line.set_alpha(0.2)
                    self.fill.set_alpha(0.2)
                    self.legline.set_alpha(0.2)
                elif state == 'invisible':
                    self.line.set_alpha(0)
                    self.fill.set_alpha(0)
                    self.legline.set_alpha(0.1)

            if state != None:
                if state in ['visible', 'transparent', 'invisible']:
                    self.state = state
                else:
                    print(f'{state} is not a valid state')

    def __init__(self, title: str, figname: str = None, autodraw: bool = True):
        self.N = 0
        self.category_labels = []
        self.data = []
        self.autodraw = autodraw
        self.feature_types = []
        self.figlines = []
        self.line_dict = {}
        self.shapes = []

        self.id = figname
        if figname == None:
            self.id = uuid.uuid1()
            
        self.title = title

        self.fig = plt.figure(self.id)

        #Code partly from https://matplotlib.org/3.1.1/gallery/event_handling/legend_picking.html
        def _on_pick(event):
            for shape in self.shapes:
                if shape.legline == event.artist:
                    if event.mouseevent.button in ['up', 'down']:
                        if shape.state == 'invisible':
                            shape.set_state('transparent')
                        else:
                            shape.set_state('invisible')
                    elif shape.state == 'visible':
                        shape.set_state('transparent')
                    elif shape.state == 'transparent':
                        shape.set_state('visible')
                else:
                    if shape.state != 'invisible':
                        shape.set_state('transparent')
                     
            plt.draw()

        self.fig.canvas.mpl_connect('pick_event', _on_pick)
        
    def add_category(self, label, tick_values: list, tick_labels: list, color='grey', size=7):
        plt.figure(self.id)

        self.category_labels.append(label)

        plt.yticks(tick_values, tick_labels, color=color, size=size)
        plt.ylim(0, 1)

        self.N += 1

        if self.autodraw:
            self.draw()

    def add_data(self, feature_type, data, color = None):
        self.data.append((data, color))

        self.feature_types.append(feature_type)

        if self.autodraw:
            self.draw()

    def draw(self):
        plt.figure(self.id)
        plt.clf()

        self.ax = plt.axes(polar=True)     
        self.ax.set_rlabel_position(0)

        plt.title(self.title)

        self.angles = [n / float(self.N) * 2 * pi for n in range(self.N)]
        self.angles += self.angles[:1]

        plt.xticks(self.angles[:-1], self.category_labels, color='grey', size=8)

        self.figlines.clear()


        self.shapes.clear()
        for i, (data, color) in enumerate(self.data):
            current_shape = self.Shape()
            lin = self.ax.plot(self.angles, data + data[:1], color=color, linewidth=1, linestyle='solid', label=self.feature_types[i], alpha=0.2)
            current_shape.set_line(lin[0])

            if color == None:
                color = lin[0].get_color()

            fill = self.ax.fill(self.angles, data + data[:1], 'b', color=color, alpha=0.2)
            current_shape.set_fill(fill[0])
            self.shapes.append(current_shape)
            
        for shape, legline in zip(self.shapes, plt.legend(loc='lower left').get_lines()): 
            shape.set_legline(legline, pick_radius=8) 

    def show(self, block=True):
        if self.autodraw:
            self.draw()
        plt.show(block=block)

if __name__ == '__main__':
    categories = ['Strength', 'Dexterity', 'Wisdom', 'Endurance', 'Luck']
    N = len(categories)
    K = 5
    d1 = [random() for _ in range(N)]
    d2 = [random() for _ in range(N)]
    d3 = [random() for _ in range(N)]

    spider_plot = SpiderPlot('title', autodraw=False)

    for category in categories:
        spider_plot.add_category(category, [k/(K - 1) for k in range(K)], [f'{100*k/(K - 1)}%' for k in range(K)])

    colors = ['green', 'red', 'blue']
    data = [d1, d2, d3]

    for color, d in zip(colors, data):
        spider_plot.add_data(color, d, color)

    spider_plot.draw()
    spider_plot.show()