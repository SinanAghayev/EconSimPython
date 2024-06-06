import tkinter as tk
from functions.graph import *

from data_types.lists import *

def initialize_new_graph(update_function, size, title=""):
    root = tk.Tk()
    g = RealTimeGraph(root, size, title)

    graph_roots.append(root)
    graph_apps.append(g)
    
    graph_update_lists.append(update_function)
    
def update_graphs(day):
    for i in range(len(graph_apps)):
        graph_apps[i].update_graph(graph_update_lists[i](), day)
        graph_roots[i].update()
        
def close_graphs():
    for root in graph_roots:
        root.destroy()
    graph_roots.clear()
    graph_apps.clear()
    graph_update_lists.clear()