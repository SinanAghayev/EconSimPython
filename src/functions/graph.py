import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

import data_types.constants as constants

class RealTimeGraph:
    def __init__(self, master, size, title=""):
        self.master = master
        self.master.title(title)

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        self.data = [[] for i in range(size)]
        self.MAX_DATA_POINTS = constants.MAX_GRAPH_DATA_POINTS

    def update_graph(self, newData, day):
        for i in range(len(newData)):
            self.data[i].append([newData[i], day])
            if len(self.data[i]) > self.MAX_DATA_POINTS or day - self.data[i][0][1] > self.MAX_DATA_POINTS:
                self.data[i].pop(0)

        self.ax.clear()
        for i in range(len(newData)):
            x = [self.data[i][j][1] for j in range(len(self.data[i]))]
            y = [self.data[i][j][0] for j in range(len(self.data[i]))]
            self.ax.plot(x, y, label=i)
        self.ax.set_title("Real-time Graph")
        self.canvas.draw()

