from jaolma.plotting.spider_plot import spider_plot
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

fig = spider_plot(
    'DND Class Stats',
    labels=['Strength', 'Dexterity', 'Intelligence', 'Speed', 'Luck'],
    silhouettes={'warrior': [15, 13, 9, 11, 10], 'thief': [9, 17, 13, 14, 15], 'mage': [3, 8, 18, 7, 12]},
    circle_label=True,
    circle_label_decimals=0,
    #scale_type='total_both',
    #axis_value_labels=False
)

size = (1000,1000)

graph = sg.Graph(canvas_size=size, graph_bottom_left=(0,0), graph_top_right=size, key='Radar', enable_events=True)

layout = [
    [graph]
]

window = sg.Window('fisk', layout, finalize=True)

figure_canvas_agg = FigureCanvasTkAgg(fig, window["Radar"].TKCanvas)
figure_canvas_agg.draw()
figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)

event, values = window.read()