import matplotlib.pyplot as plt

import numpy as np

from math import pi, ceil

import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from jaolma.utility.utility import prints

class Axis:
    def __init__(self, values, label: str = '', axis_min: float = None, axis_max: float = None):
        if axis_min == None:
            if len(values) == 0:
                self.min = 0
            else:
                self.min = min(values)
        else:
            self.min = axis_min

        if axis_max == None:
            if len(values) == 0:
                self.max = 1
            else:
                self.max = max(values)
        else:
            self.max = axis_max

        self.label = label
        self.scaled = (min != 0 or max != 1)
        self.values = values
        self.norm = [self.normalize(v) for v in values]

    def normalize(self, value):
        return (value - self.min) / (self.max - self.min)

# title
# labels: list of labels for each axis. e.g. ['strength', 'dexterity', 'intelligence']
# silhouettes: dictionary containing list of values with silhouette label as key. e.g. {'warrior': [15, 13, 9], 'thief': [9, 17, 13], 'mage': [3, 8, 18]}
# scale_type: 
#   'total_max': scales all axes to the total max value. 
#   'total_both': scales both min and max to the total min and max values.
#   'axis_max': scales axes to the max value of that axis. 
#   'axis_both': scales axes to the min and max values of that one axis.
#   'set': uses the axis_max and axis_min values (or lists) to set max and min.

def spider_plot(title: str, labels: list, silhouettes: dict, axis_min: float = None, axis_max: float = None, axis_value_decimals: int = 3, axis_value_labels: bool = True, circle_n: int = None, circle_label: bool = True, circle_label_decimals: int = None, circle_label_size: int = 8, scale_type: str = 'total_max', label_origin: bool = True, silhouette_line_color: str = None, silhouette_line_style: str = 'solid', silhouette_line_size: float = 1, silhouette_fill_color: str = None, silhouette_fill_alpha: float = 0.1, silhouette_value_labels: list = None):
    fig = plt.figure(figsize=(10,10), dpi=100)
    ax = plt.axes(projection='polar')
    ax.set_ylim(0, 1)
    fig.suptitle(title)

    if len(silhouettes) == 0:
        raise Exception('Length of silhouettes should be one or above.')

    n_silhouettes = len(silhouettes)
    n_values = len(list(silhouettes.values())[0])

    if n_values < 1:
        raise Exception('There should be at least one axis.')

    for silhouette in silhouettes.values():
        if len(silhouette) != n_values:
            raise Exception('All silhouettes must have the same amount of axes.')

    # Making axes - primarily code for scaling data along them.
    axes = []
    angles = []
    for i in range(n_values):
        values = [list(silhouettes.values())[j][i] for j in range(n_silhouettes)]

        current_axis_min = None
        current_axis_max = None

        if scale_type == 'axis_max':
            current_axis_min = 0
            pass

        elif scale_type == 'total_max':
            current_axis_min = 0
            current_axis_max = max([max(vals) for vals in silhouettes.values()])
            pass

        elif scale_type == 'axis_both':
            # Default in Axis __init__.
            prints('WARNING: Different minimum values - be careful.', tag='spider_plot')
            pass

        elif scale_type == 'total_both':
            current_axis_min = min([min(vals) for vals in silhouettes.values()])
            current_axis_max = max([max(vals) for vals in silhouettes.values()])
            pass

        elif scale_type == 'set':
            if isinstance(axis_min, list):
                if len(axis_min) != n_values:
                    raise Exception('axis_min should be value or have one value for each axis.')
                current_axis_min = axis_min[i]

                if current_axis_min == None:
                    current_axis_min = min(values)

            if isinstance(axis_max, list):
                if len(axis_max) != n_values:
                    raise Exception('axis_max should be value or have one value for each axis.')
                current_axis_max = axis_max[i]

                if current_axis_max == None:
                    current_axis_max = max(values)

        else:
            raise Exception('scale_type not understood.')

        if (current_axis_min != None and current_axis_max != None) and (current_axis_min >= current_axis_max):
            raise Exception('Axis max-min is 0 or negative.')

        axis = Axis(values=values, label=labels[i], axis_min=current_axis_min, axis_max=current_axis_max)
        angle = 2 * pi * i / float(n_values)

        axes.append(axis)
        angles.append(angle)

    same_axes = all([ax.min == axes[0].min and ax.max == axes[0].max for ax in axes])

    # Draws circles.
    if circle_n != 0 and (same_axes or circle_n != None):
        if circle_n == None:
            circle_n = 4
            for i in [6, 5, 8, 4, 7, 9, 3]:
                if int(axes[0].max - axes[0].min) % i == 0:
                    circle_n = i - 1
                    if circle_label_decimals == None:
                        circle_label_decimals = 0
                    break

        axis = axes[0]
        values = np.linspace(axis.min, axis.max, circle_n + 2)

        ax.set_yticks([axis.normalize(val) for val in values])

        if circle_label == True:
            if circle_label_decimals == None:
                circle_label_decimals = 1
            yticklabels = [f'{{:.{circle_label_decimals}f}}'.format(val) for val in values]
            ax.set_yticklabels(yticklabels, size=circle_label_size)
        else:
            ax.set_yticklabels([])

    else:
        if all([ax.min == axes[0].min for ax in axes]) and label_origin:
            ax.set_yticks([0])
            if circle_label_decimals == None:
                circle_label_decimals = 1
            ax.set_yticklabels([f'{axes[0].min}'], size=circle_label_size)

        else:
            ax.set_yticks([])

    _, tick_labels = plt.xticks(angles, ['' for _ in angles])
    
    for label, angle, text in zip(tick_labels, angles, labels):
        rotation = angle*180/pi-90

        # Rotates text so it can be read when its supposed to be upside down.
        if rotation < -90 or rotation > 90:
            rotation += 180

        plt.text(angle, 0, text, 
            transform=label.get_transform(), 
            ha=label.get_ha(), 
            va=label.get_va(),
            rotation=rotation, 
            size=12, 
            color='black')

    curved_angles = []

    for angle in angles:
        curved_angles.extend(np.arange(angle, angle + 2 * pi / n_values, 0.01))

    angles += angles[:1]
    curved_angles += angles[:1]
 
    for i in range(n_silhouettes):
        values = [ax.norm[i] for ax in axes]
        values += values[:1]
        
        if axis_value_labels != False:
            for j in range(n_values):
                if axis_value_labels == True:
                    label = str(axes[j].values[i])
                else:
                    label = axis_value_labels[i][j]

                if label != None:
                    plt.text(angles[j], values[j], label, color="black", size=8)
   
        curved_values = []
        for a, b in zip(values[:-1], values[1:]):
            curved_values.extend(np.linspace(a, b, ceil(2*np.pi/n_values/0.01+1))[:-1])
        curved_values += values[:1]

        if silhouette_line_color == None:
            line_color = None
        elif isinstance(silhouette_line_color, list):
            line_color = silhouette_line_color[i]
        else:
            line_color = silhouette_line_color

        if silhouette_fill_color == None:
            fill_color = line.get_color()
        elif isinstance(silhouette_fill_color, list):
            fill_color = silhouette_fill_color[i]
        else:
            fill_color = silhouette_fill_color

        line = ax.plot(curved_angles, curved_values, color=line_color, linewidth=silhouette_line_size, linestyle=silhouette_line_style, label=list(silhouettes.keys())[i])[0]
        ax.fill(curved_angles, curved_values, color=fill_color, alpha=silhouette_fill_alpha)

    plt.legend()
    return fig
