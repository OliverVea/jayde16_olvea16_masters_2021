import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

class DraggablePolygon:
    lock = None
    def __init__(self):
        print('__init__')
        self.press = None

        fig = plt.figure()
        ax = fig.add_subplot(111)

        self.geometry = [[[0.0,0.0],[0.2,0.0],[0.2,0.2],[0.0,0.2]], [[0.5,0.5],[0.7,0.5],[0.7,0.7],[0.5,0.7]]]
        self.newGeometry = []

        poly = [plt.Polygon(self.geometry[0], closed=True, fill=False, linewidth=3, color='#F97306'), plt.Polygon(self.geometry[0], closed=True, fill=False, linewidth=3, color='#F97306')]

        for p in poly:
            ax.add_patch(p)

        self.poly = poly

    def connect(self):
        'connect to all the events we need'
        print('connect')

        for p in self.poly:
            self.cidpress = p.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)
            self.cidrelease = p.figure.canvas.mpl_connect(
            'button_release_event', self.on_release)
            self.cidmotion = p.figure.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)

    def on_press(self, event):
        'on button press we will see if the mouse is over us and store some data'
        print('on_press')
        if event.inaxes != self.poly[0].axes: return
        if DraggablePolygon.lock is not None: return

        for i, p in enumerate(self.poly):
            contains, attrd = p.contains(event)
            if not contains: return

            if not self.newGeometry:
                x0, y0 = self.geometry[i][0]
            else:
                x0, y0 = self.newGeometry[i][0]

            self.press = x0, y0, event.xdata, event.ydata
            DraggablePolygon.lock = i

    def on_motion(self, event):
        'on motion we will move the rect if the mouse is over us'
        if DraggablePolygon.lock is None:
            return

        i = DraggablePolygon.lock

        if event.inaxes != self.poly[i].axes: return
        x0, y0, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress

        xdx = [i+dx for i,_ in self.geometry[i]]
        ydy = [i+dy for _,i in self.geometry[i]]
        self.geometry[i] = [[a, b] for a, b in zip(xdx, ydy)]
        self.poly[i].set_xy(self.geometry[i])
        self.poly[i].figure.canvas.draw()

    def on_release(self, event):
        'on release we reset the press data'
        print('on_release')
        if DraggablePolygon.lock is None:
            return

        self.press = None
        DraggablePolygon.lock = None
        self.geometry = self.newGeometry


    def disconnect(self):
        'disconnect all the stored connection ids'
        print('disconnect')
        for p in self.poly:
            p.figure.canvas.mpl_disconnect(self.cidpress)
            p.figure.canvas.mpl_disconnect(self.cidrelease)
            p.figure.canvas.mpl_disconnect(self.cidmotion)


dp = DraggablePolygon()
dp.connect()

plt.show()