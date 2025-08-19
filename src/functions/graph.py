import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

import data_types.constants as constants

from mpl_toolkits.mplot3d import Axes3D
import numpy as np


class RealTimeGraph:
    graph_count = 0

    def __init__(self, master, size, title=""):
        self.master = master
        self.master.title(title)

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        self.data = [[] for i in range(size)]
        self.MAX_DATA_POINTS = constants.MAX_GRAPH_DATA_POINTS

        self.master.update_idletasks()  # Important to get correct size
        width = self.master.winfo_width()
        height = self.master.winfo_height()

        self.master.geometry(
            f"+{(self.graph_count % 3) * width}+{(self.graph_count // 3) * height}"
        )

        RealTimeGraph.graph_count += 1

    def update_graph(self, newData, day):
        for i in range(len(newData)):
            self.data[i].append([newData[i], day])
            if (
                len(self.data[i]) > self.MAX_DATA_POINTS
                or day - self.data[i][0][1] > self.MAX_DATA_POINTS
            ):
                self.data[i].pop(0)

        self.ax.clear()
        for i in range(len(newData)):
            x = [self.data[i][j][1] for j in range(len(self.data[i]))]
            y = [self.data[i][j][0] for j in range(len(self.data[i]))]
            self.ax.plot(x, y, label=i)
        self.ax.set_title("Real-time Graph")
        self.canvas.draw()


class RealTimeGraph3D:
    graph_count = 0

    def __init__(self, master, title="Gaussian 3D"):
        self.master = master
        self.master.title(title)

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        self.history = []
        self.MAX_HISTORY = constants.MAX_GRAPH_DATA_POINTS
        RealTimeGraph3D.graph_count += 1

    def update_graph(self, newData, day, resolution=50, x_range=(-5, 5)):
        # Add new Gaussian parameters
        print(f"Updating 3D graph with data: {newData}, day: {day}")
        self.history.append((newData[0][0], newData[0][1], day))
        if len(self.history) > self.MAX_HISTORY:
            self.history.pop(0)

        self.ax.clear()

        means, stds, days = zip(*self.history)
        x = np.linspace(x_range[0], x_range[1], resolution)
        y = np.array(days)

        X, Y = np.meshgrid(x, y)

        # Compute Z values (PDFs for each day)
        Z = np.zeros_like(X)
        for i, (m, s, d) in enumerate(self.history):
            Z[i, :] = (1 / (s * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - m) / s) ** 2)

        # Plot surface
        self.ax.plot_surface(X, Y, Z, cmap="viridis", alpha=0.8)

        self.ax.set_title("Gaussian Distribution Evolution (Surface)")
        self.ax.set_xlabel("X (variable)")
        self.ax.set_ylabel("PDF")
        self.ax.set_zlabel("Day")

        self.canvas.draw()
