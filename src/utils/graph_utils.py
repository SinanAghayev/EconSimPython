import tkinter as tk
import matplotlib.pyplot as plt

from src.utils.graph import RealTimeGraph, RealTimeGraph3D
from src.data_types.graph_state import graph_apps, graph_roots, graph_update_lists


def initialize_new_graph(update_function, size, title=""):
    root = tk.Tk()
    g = RealTimeGraph(root, size, title)

    graph_roots.append(root)
    graph_apps.append(g)
    graph_update_lists.append(update_function)


def initialize_new_graph_3d(update_function, title="3D Gaussian"):
    root = tk.Tk()
    g = RealTimeGraph3D(root, title)

    graph_roots.append(root)
    graph_apps.append(g)
    graph_update_lists.append(update_function)


def update_graphs(day):
    for i in range(len(graph_apps)):
        graph_apps[i].update_graph(graph_update_lists[i](), day)
        graph_roots[i].update()


def close_graphs():
    plt.close("all")
    for root in graph_roots:
        root.destroy()
    graph_roots.clear()
    graph_apps.clear()
    graph_update_lists.clear()
