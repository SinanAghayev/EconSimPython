import sys
import os

from data_types.constants import *
from data_types.lists import *

from functions.initialize import *
from functions.update_functions import *
from functions.io_functions import *
from functions.graph_functions import *

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

show_index = 0


def episode(i):
    RealTimeGraph.graph_count = 0
    day = 0
    start()
    print(f"Episode {i} started")

    p = allPeople[0]
    initialize_new_graph(
        lambda: [
            person.balance / p.country.currency.exchangeRate[person.country.currency]
            for person in allPeople
        ],
        PEOPLE_COUNT,
        "People Balance",
    )
    """
    initialize_new_graph(
        lambda: [serv.price for serv in allPeople[show_index].personServices],
        len(allPeople[show_index].personServices),
        "Service Price",
    )
    initialize_new_graph(
        lambda: [serv.demand for serv in allPeople[show_index].personServices],
        len(allPeople[show_index].personServices),
        "Service Demand",
    )
    initialize_new_graph(
        lambda: [serv.supply for serv in allPeople[show_index].personServices],
        len(allPeople[show_index].personServices),
        "Service Supply",
    )
    initialize_new_graph(
        lambda: [
            serv.bought_recently_count for serv in allPeople[show_index].personServices
        ],
        len(allPeople[show_index].personServices),
        "Service Bought Recently Count",
    )
    initialize_new_graph(
        lambda: [serv.revenue for serv in allPeople[show_index].personServices],
        len(allPeople[show_index].personServices),
        "Service Revenue",
    )"""

    initialize_new_graph(
        lambda: [c.balance for c in allCountries], COUNTRY_COUNT, "Country Balance"
    )
    initialize_new_graph(
        lambda: [c.inflation for c in allCountries], COUNTRY_COUNT, "Country Inflation"
    )
    initialize_new_graph(
        lambda: [c.value for c in allCurrencies], COUNTRY_COUNT, "Currency Value"
    )

    while True:
        update(day)
        if keyboard_constants["visualize"]:
            update_graphs(day)
        check_keyboard()
        after_update()

        # print("Day: ", day)
        if day % 50 == 0:
            print("Day: ", day, " Balance: ", allPeople[0].balance)

        # if (day + 1) % 50 == 0 and aiPersonExists:
        #     allPeople[0].alpha *= 0.9
        if (day + 1) % MAX_DAY == 0:
            close_graphs()
            print(f"AI balance: {allPeople[0].balance}")
            break

        day += 1

    print("Backpropagating...")
    allPeople[0].backpropagate()


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
