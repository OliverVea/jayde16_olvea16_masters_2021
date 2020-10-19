import matplotlib.pyplot as plt
import uuid
from math import pi
from jaolma.utility.utility import transpose, linspace

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
                    self.line.set_alpha(1)
                    self.fill.set_alpha(0.8)
                    self.legline.set_alpha(1)
                elif state == 'transparent':
                    self.line.set_alpha(1)
                    self.fill.set_alpha(0.1)
                    self.legline.set_alpha(0.75)
                elif state == 'invisible':
                    self.line.set_alpha(0)
                    self.fill.set_alpha(0)
                    self.legline.set_alpha(0.1)

            if state != None:
                if state in ['visible', 'transparent', 'invisible']:
                    self.state = state
                else:
                    print(f'{state} is not a valid state')

    def __init__(self, title: str, figname: str = None, autodraw: bool = True, scale_plot: bool = False, figsize: tuple = None):
        self.N = 0
        self.figsize = figsize
        self.category_labels = []
        self.data = []
        self.color = []
        self.autodraw = autodraw
        self.feature_types = []
        self.figlines = []
        self.line_dict = {}
        self.shapes = []
        self.tick_values = {}
        self.tick_labels = {}
        self.scale_plot = scale_plot

        self.id = figname
        if figname == None:
            self.id = uuid.uuid1()
            
        self.title = title

        self.fig = plt.figure(self.id, figsize=figsize)

        

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
                    elif shape.state in ['transparent', 'invisible']:
                        shape.set_state('visible')
                else:
                    if shape.state != 'invisible':
                        shape.set_state('transparent')
                     
            plt.draw()

        self.fig.canvas.mpl_connect('pick_event', _on_pick)
        
    def add_category(self, label, tick_values: list, tick_labels: list):
        plt.figure(self.id)

        self.category_labels.append(label)

        self.tick_labels[label] = tick_labels
        self.tick_values[label] = tick_values

        self.N += 1

        if self.autodraw:
            self.draw()

    def add_data(self, feature_type, data, color = None):
        self.data.append(data)
        self.color.append(color)

        self.feature_types.append(feature_type)

        if self.autodraw:
            self.draw()

    def draw(self, min_percentage: float = 0.2):
        plt.figure(self.id)
        plt.clf()

        self.ax = plt.axes(polar=True)     
        self.ax.set_rlabel_position(0)

        plt.ylim(0, 1)
        
        plt.title(self.title, size=self.figsize[0]*2)

        self.angles = [n / float(self.N) * 2 * pi for n in range(self.N)]
        self.angles += self.angles[:1]

        #locs, labels = plt.xticks(self.angles[:-1], self.category_labels, color='black', size=self.figsize[0])
        plt.xticks(self.angles[:-1], '', color='black', size=self.figsize[0])
        for angle, category in zip(self.angles, self.category_labels):
            plt.text(angle-0.03, 1.05, category, color="black", size=self.figsize[0], horizontalalignment='center', verticalalignment='center')

        self.figlines.clear()
        
        self.shapes.clear()

        data = [[e for e in row] for row in self.data]

        for i, (label, angle, d) in enumerate(zip(self.tick_values, self.angles[:-1], transpose(data))):
            p = None

            if self.tick_values[label] == None:
                if self.scale_plot:
                    mi, ma = min(d), max(d)
                else:
                    mi, ma = 0, 1

                if mi == ma: 
                    p = min_percentage
                    mi = min(mi,min_percentage)
                    ma = max(ma,1) 

                tick_values = linspace(mi, ma, 5)
            else:
                tick_values = self.tick_values[label].copy()

            if self.scale_plot:
                scale = lambda val, mi, ma, a: (val - mi) / (ma - mi) * (1 - a) + a

                if len(tick_values) != 0 and min(d) > min(tick_values) and p == None:
                    p = 0
                elif p == None:
                    p = min_percentage

                mi = min(d + tick_values)
                ma = max(d + tick_values)
                if mi == ma: 
                    p = min_percentage
                    mi = min(mi,min_percentage)
                    ma = max(ma,1)

                tick_values = [scale(tick_value, mi, ma, p) for tick_value in tick_values]
                    
                for j, e in enumerate(d):
                    data[j][i] = scale(e, mi, ma, p)

            if self.tick_labels[label] == None:
                tick_labels = [f'{tick_value * (ma - mi) + mi:.3g}' for tick_value in tick_values]
            else:
                tick_labels = self.tick_labels[label].copy()

            plt.yticks(tick_values)
            for tick_value, tick_label in zip(tick_values, tick_labels):
                plt.text(angle, tick_value, tick_label, color="black", size=self.figsize[0])

            plt.tick_params(axis='y', labelleft=False)

        for i, (d, color) in enumerate(zip(data, self.color)):
            current_shape = self.Shape()
            lin = self.ax.plot(self.angles, d + d[:1], color=color, linewidth=1, linestyle='solid', label=self.feature_types[i])
            current_shape.set_line(lin[0])

            if color == None:
                color = lin[0].get_color()

            fill = self.ax.fill(self.angles, d + d[:1], 'b', color=color, alpha=0.2)
            current_shape.set_fill(fill[0])
            self.shapes.append(current_shape)
            
        for shape, legline in zip(self.shapes, plt.legend(loc='lower left', bbox_to_anchor=(0, -0.1)).get_lines()):
            legline.set_alpha(0.5)
            shape.set_legline(legline, pick_radius=8) 

    def show(self, dpi: int = 300, show: bool = True, save_png: bool = False, save_pdf: bool = False, block=True):
        if self.autodraw:
            self.draw()

        plt.figure(self.id)

        if save_pdf:
            plt.savefig(f'output/{self.id}.pdf', dpi=dpi)

        if save_png:
            plt.savefig(f'output/{self.id}.png', dpi=dpi)

        if show:
            plt.show(block=block)