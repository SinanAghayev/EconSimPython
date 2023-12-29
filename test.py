import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import random


class RealTimeGraph:
    def __init__(self, master, size):
        self.master = master
        self.master.title("Real-time Graph")

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        self.data = [[] for i in range(size)]
        self.MAX_DATA_POINTS = 50
        self.day = 1

    def update_graph(self, newData):
        for i in range(len(newData)):
            self.data[i].append(newData[i])
            if len(self.data[i]) > self.MAX_DATA_POINTS:
                self.data[i].pop(0)

        self.ax.clear()
        for i in range(len(newData)):
            self.ax.plot(
                range(max(0, self.day - self.MAX_DATA_POINTS), self.day),
                self.data[i],
                label=i,
            )
        self.ax.set_title("Real-time Graph")
        self.canvas.draw()
        self.day += 1
