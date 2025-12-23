import sys
import os

import src.data_types.constants as constants
import src.data_types.config as config
import src.data_types.statistics as statistics
import src.data_types.data_collections as data_collections

import src.functions.initialize as initialize
import src.functions.update_functions as update_functions
import src.functions.io_functions as io_functions
import src.functions.graph_functions as graph_functions
from src.functions.graph import RealTimeGraph

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

show_index = 0


def episode(i):
    RealTimeGraph.graph_count = 0
    day = 0
    initialize.start()
    print(f"Episode {i} started")

    p = data_collections.all_people[0]
    graph_functions.initialize_new_graph(
        lambda: [
            person.balance / p.country.currency.exchangeRate[person.country.currency]
            for person in data_collections.all_people
        ],
        constants.PEOPLE_COUNT,
        "People Balance",
    )
    """"""
    graph_functions.initialize_new_graph(
        lambda: [
            serv.price
            for serv in data_collections.all_people[show_index].personServices
        ],
        len(data_collections.all_people[show_index].personServices),
        "Service Price",
    )
    """
    initialize_new_graph(
        lambda: [serv.demand for serv in allPeople[show_index].personServices],
        len(allPeople[show_index].personServices),
        "Service Demand",
    )"""
    graph_functions.initialize_new_graph(
        lambda: [
            serv.supplyBeforeSales
            for serv in data_collections.all_people[show_index].personServices
        ],
        len(data_collections.all_people[show_index].personServices),
        "Service Supply",
    )

    graph_functions.initialize_new_graph(
        lambda: [
            serv.bought_recently_count
            for serv in data_collections.all_people[show_index].personServices
        ],
        len(data_collections.all_people[show_index].personServices),
        "Service Bought Recently Count",
    )
    """
    initialize_new_graph(
        lambda: [serv.revenue for serv in allPeople[show_index].personServices],
        len(allPeople[show_index].personServices),
        "Service Revenue",
    )"""
    """
    initialize_new_graph(
        lambda: [c.balance for c in allCountries], COUNTRY_COUNT, "Country Balance"
    )
    initialize_new_graph(
        lambda: [c.inflation for c in allCountries], COUNTRY_COUNT, "Country Inflation"
    )
    initialize_new_graph(
        lambda: [c.value for c in allCurrencies], COUNTRY_COUNT, "Currency Value"
    )"""
    graph_functions.initialize_new_graph_3d(
        lambda: statistics.mean_std,  # Assuming the first person is the AI
    )

    while True:
        update_functions.update(day)
        if config.VISUALIZE_GRAPHS:
            update_functions.update_graphs(day)
        io_functions.check_keyboard()
        update_functions.after_update()

        # print("Day: ", day)
        if day % 50 == 0:
            print("Day: ", day, " Balance: ", data_collections.all_people[0].balance)

        # if (day + 1) % 50 == 0 and aiPersonExists:
        #     allPeople[0].alpha *= 0.9
        if (day + 1) % constants.MAX_DAY == 0:
            graph_functions.close_graphs()
            print(f"AI balance: {data_collections.all_people[0].balance}")
            break

        day += 1

    print("Backpropagating...")
    data_collections.all_people[0].backpropagate()


print("Starting simulation...")
i = 0
while True:
    episode(i)
    print(f"Episode {i} finished")

    data_collections.all_people[0].save()
    print("Network data saved")

    io_functions.write_data_to_file()
    print("Data written to files")

    i += 1
    read_from_file = True
