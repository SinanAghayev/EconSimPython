import sys
import os
import random
import shutil

import tkinter as tk

from data_types.currency_class import Currency
from data_types.country_class import Country
from data_types.service_class import Service
from data_types.person_class import Person
from data_types.person_ai_class import PersonAI

from data_types.constants import *
from data_types.lists import *

from functions.initialize import *
from functions.update_functions import *
from functions.io_functions import *
from functions.graph_functions import *

from functions.graph import RealTimeGraph

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

show_index = 0

def episode(i):
    day = 0
    start()
    print(f"Episode {i} started")

    initialize_new_graph(lambda: [person.balance for person in allPeople], PEOPLE_COUNT, "People Balance")
    initialize_new_graph(lambda: [serv.price for serv in allPeople[show_index].personServices], len(allPeople[show_index].personServices), "Service Price")
    initialize_new_graph(lambda: [serv.demand for serv in allPeople[show_index].personServices], len(allPeople[show_index].personServices), "Service Demand")
    initialize_new_graph(lambda: [serv.supply for serv in allPeople[show_index].personServices], len(allPeople[show_index].personServices), "Service Supply")

    while True:
        update(day)
        if keyboard_constants["visualize"]:
            update_graphs(day)
        check_keyboard()

        print("Day: ", day)

        if (day + 1) % 50 == 0 and aiPersonExists:
            allPeople[0].alpha *= 0.9
        if (day + 1) % MAX_DAY == 0:
            close_graphs()
            print(f"AI balance: {allPeople[0].balance}")
            break

        day += 1


print("Starting simulation...")
i = 0
while True:
    episode(i)
    print(f"Episode {i} finished")

    allPeople[0].save()
    print("Network data saved")

    write_data()
    print("Data written to files")

    i += 1
    read_from_file = True

