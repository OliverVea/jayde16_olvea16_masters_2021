from jaolma.plotting.spider_plot import spider_plot
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

axis_min = [0, 0, 0, 0, 0]
axis_max = [19, 19, 19, 19, 19]

silhouettes = {'Warrior': [15, 13, 9, 11, 10], 'Thief': [9, 17, 13, 14, 15], 'Mage': [3, 8, 18, 7, 12]}

axis_value_labels = [['se', 'man', 'kan', 'også', 'skrive'], ['vilkårlige', 'labels', 'hvis', 'man', 'har'], ['lyst', '.', ':D', None, None]]
axis_value_labels = True

if True:
    silhouettes['Warrior'].append(350)
    silhouettes['Thief'].append(150)
    silhouettes['Mage'].append(900)

    axis_min.append(0)
    axis_max.append(1000)

    if isinstance(axis_value_labels, list):
        axis_value_labels[0].append(None)
        axis_value_labels[1].append(None)
        axis_value_labels[2].append(None)

fig = spider_plot(
    'DND Class Stats',
    labels=['Strength', 'Dexterity', 'Intelligence', 'Speed', 'Luck', 'Gold'],
    silhouettes=silhouettes,
    #circle_label=False,
    #circle_label_decimals=0,
    axis_value_labels=axis_value_labels,
    #circle_n=5,
    scale_type='set',
    axis_min=axis_min,
    axis_max=axis_max,
    silhouette_line_color=['y', (1, 0.6, 0.6), 'teal'],
    silhouette_fill_color=[(1, 0.6, 0.6), 'teal', 'y'],
    silhouette_line_size=1.5,
    silhouette_line_style='-.',
    silhouette_fill_alpha=0.25,
)

size = (1000,1000)

graph = sg.Graph(canvas_size=size, graph_bottom_left=(0,0), graph_top_right=size, key='Radar', enable_events=True)

layout = [[graph]]

window = sg.Window('fisk', layout, finalize=True)

figure_canvas_agg = FigureCanvasTkAgg(fig, window['Radar'].TKCanvas)
figure_canvas_agg.draw()
figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)

event, values = window.read()