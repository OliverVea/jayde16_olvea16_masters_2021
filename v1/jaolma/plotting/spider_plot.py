import matplotlib.pyplot as plt
import uuid
from math import pi
from jaolma.utility.utility import transpose

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

    def __init__(self, title: str, figname: str = None, autodraw: bool = True, scale_plot: bool = False):
        self.N = 0
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
                    elif shape.state in ['transparent', 'invisible']:
                        shape.set_state('visible')
                else:
                    if shape.state != 'invisible':
                        shape.set_state('transparent')
                     
            plt.draw()

        self.fig.canvas.mpl_connect('pick_event', _on_pick)
        
    def add_category(self, label, tick_values: list, tick_labels: list, color='grey', size=7):
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

    def draw(self):
        plt.figure(self.id)
        plt.clf()


        self.ax = plt.axes(polar=True)     
        self.ax.set_rlabel_position(0)
        
        plt.title(self.title)

        self.angles = [n / float(self.N) * 2 * pi for n in range(self.N)]
        self.angles += self.angles[:1]

        plt.xticks(self.angles[:-1], self.category_labels, color='grey', size=10)

        self.figlines.clear()
        
        self.shapes.clear()

        for i, (label, angle, data) in enumerate(zip(self.tick_values, self.angles[:-1], transpose(self.data))):
            if self.scale_plot:
                min_tick_value = min(data + self.tick_values[label])
                max_tick_value = max(data + self.tick_values[label])
                y_lim_lower = min_tick_value - (max_tick_value - min_tick_value) * 0.2
                y_lim_upper = max_tick_value
                for j, elem in enumerate(self.data):
                    elem[i] = (data[j] - min_tick_value) / (max_tick_value - min_tick_value) * 0.8 + 0.2

            for tick_value, tick_label in zip(self.tick_values[label], self.tick_labels[label]):
                plt.text(angle, tick_value, tick_label, color="grey", size=7)

            plt.tick_params(axis='y', labelleft=False)


        for i, (data, color) in enumerate(zip(self.data, self.color)):
            current_shape = self.Shape()
            lin = self.ax.plot(self.angles, data + data[:1], color=color, linewidth=1, linestyle='solid', label=self.feature_types[i])
            current_shape.set_line(lin[0])

            if color == None:
                color = lin[0].get_color()

            fill = self.ax.fill(self.angles, data + data[:1], 'b', color=color, alpha=0.2)
            current_shape.set_fill(fill[0])
            self.shapes.append(current_shape)
            
        for shape, legline in zip(self.shapes, plt.legend(loc='lower left').get_lines()):
            legline.set_alpha(0.5)
            shape.set_legline(legline, pick_radius=8) 

    def show(self, block=True):
        if self.autodraw:
            self.draw()
        plt.show(block=block)