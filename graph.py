import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from constants import *

name = [
    "Country ",
    "Currency ",
    "Person ",
    "Service ",
]

countOfItems = [COUNTRY_COUNT, COUNTRY_COUNT, PEOPLE_COUNT, SERVICE_COUNT]

root = tk.Tk()


def is_numeric(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def update_graph_choices(*args):
    file_index = file_var.get()

    if file_index == "Country":
        graph_choices = [
            "1 - Balance",
            "2 - GDP",
            "3 - Balance in Currency 0",
            "4 - GDP in Currency 0",
            "5 - Inflation",
        ]
    elif file_index == "Currency":
        graph_choices = ["1 - Value", "2 - Demand", "3 - Supply"]
    elif file_index == "People":
        graph_choices = [
            "1 - Balance",
            "2 - Balance in Currency 0",
            "3 - Save Urge",
            "4 - Country",
            "5 - Age",
            "6 - Bought Services",
        ]
    elif file_index == "Services":
        graph_choices = [
            "1 - Base Price",
            "2 - Price",
            "3 - Price in Currency 0",
            "4 - Demand",
            "5 - Supply",
            "6 - Overall Services Bought",
            "7 - Type",
            "8 - Revenue",
        ]
    else:
        graph_choices = []

    graph_combo["values"] = graph_choices
    if graph_choices:
        graph_combo.current(0)


def show_graph(file_index, graph_type, day_count, indices=[]):
    f = int(file_index)
    d = int(day_count)

    # Clear the existing plot
    plt.clf()

    if indices == []:
        indices = [i for i in range(countOfItems[f])]

    fig = plt.figure()
    for i in indices:
        days = np.array([])
        data = np.array([])

        for j in range(d):
            temp = [
                float(k.replace(".", "").replace(",", "."))
                for k in a[j + 1].strip().split(" ")
                if is_numeric(k.replace(".", "").replace(",", "."))
            ]
            days = np.append(days, temp[0])
            data = np.append(data, temp[graph_type])

        plt.plot(days, data, label=name[f] + str(i))

    plt.legend()

    # Create a canvas to display the graph
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()

    # Remove previous canvas, if any
    if hasattr(root, "canvas"):
        root.canvas.get_tk_widget().pack_forget()
    root.canvas = canvas

    # Pack the canvas
    canvas.get_tk_widget().pack()


def handle_input(event=None):
    file_names = {"Country": 0, "Currency": 1, "People": 2, "Services": 3}

    file_index = file_names[file_var.get()]
    graph_type = int(graph_var.get().split(" - ")[0])
    day_count = days_slider.get()

    indices_input = indices_entry.get()
    indices = parse_indices(indices_input)

    show_graph(file_index, graph_type, day_count, indices)


def parse_indices(indices_input):
    indices = []
    if indices_input.strip() == "":
        return indices  # Return an empty list if no input is given

    indices_list = indices_input.strip().split(",")
    for index_item in indices_list:
        index_range = index_item.strip().split("-")
        if len(index_range) == 1:
            indices.append(int(index_range[0]))
        elif len(index_range) == 2:
            start_index = int(index_range[0])
            end_index = int(index_range[1])
            indices.extend(range(start_index, end_index + 1))
    return indices


# Create GUI elements
label = tk.Label(root, text="Select graph options:")
label.pack()

# File selection
file_label = tk.Label(root, text="File:")
file_label.pack()
file_var = tk.StringVar()
file_combo = ttk.Combobox(
    root, textvariable=file_var, values=["Country", "Currency", "People", "Services"]
)
file_combo.pack()
file_combo.bind("<<ComboboxSelected>>", update_graph_choices)


# Graph type selection
graph_label = tk.Label(root, text="Graph Type:")
graph_label.pack()
graph_var = tk.StringVar()
graph_combo = ttk.Combobox(root, textvariable=graph_var, state="readonly")
graph_combo.pack()

# Days slider
days_label = tk.Label(root, text="Day Count:")
days_label.pack()
days_slider = tk.Scale(root, from_=0, to=MAX_DAY, orient=tk.HORIZONTAL)
days_slider.pack()
days_slider.set(MAX_DAY)

# Create the indices entry widget
indices_label = tk.Label(root, text="Indices (comma-separated):")
indices_label.pack()
indices_entry = tk.Entry(root)
indices_entry.pack()

# Show Graph button
button = tk.Button(root, text="Show Graph", command=handle_input)
button.pack()

# Update the graph choices based on the selected file index
update_graph_choices()

# Set the default values for the sliders and combobox
file_var.set(0)
graph_var.set("1 - Balance")

# Create initial graph
show_graph(0, 0, 10)

root.mainloop()
