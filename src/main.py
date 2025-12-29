import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import src.data_types.constants as constants
import src.data_types.config as config
import src.data_types.data_collections as data_collections

import src.utils.initialize as initialize
import src.utils.update_utils as update_utils
import src.utils.io_utils as io_utils
import src.utils.graph_utils as graph_utils
from src.utils.graph import RealTimeGraph

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

show_index = 0


def episode(i):
    RealTimeGraph.graph_count = 0
    day = 0
    initialize.start()
    print(f"Episode {i} started")

    p = data_collections.all_people[0]
    # Balance of people
    graph_utils.initialize_new_graph(
        lambda: [
            person.balance / p.country.currency.exchange_rate[person.country.currency]
            for person in data_collections.all_people
        ],
        constants.PEOPLE_COUNT,
        "People Balance",
    )
    # Prices of services of given person
    graph_utils.initialize_new_graph(
        lambda: [
            service.price
            for service in data_collections.all_people[show_index].provided_services
        ],
        len(data_collections.all_people[show_index].provided_services),
        "Service Price",
    )
    # Demands of services of given person
    graph_utils.initialize_new_graph(
        lambda: [
            service.demand
            for service in data_collections.all_people[show_index].provided_services
        ],
        len(data_collections.all_people[show_index].provided_services),
        "Service Demand",
    )
    # Supplies of services of given person
    graph_utils.initialize_new_graph(
        lambda: [
            service.supply_before_sales
            for service in data_collections.all_people[show_index].provided_services
        ],
        len(data_collections.all_people[show_index].provided_services),
        "Service Supply",
    )
    # Count of recently bought services of given person
    graph_utils.initialize_new_graph(
        lambda: [
            serv.bought_recently_count
            for serv in data_collections.all_people[show_index].provided_services
        ],
        len(data_collections.all_people[show_index].provided_services),
        "Service Bought Recently Count",
    )
    # Revenues from services of given person
    graph_utils.initialize_new_graph(
        lambda: [
            service.revenue
            for service in data_collections.all_people[show_index].provided_services
        ],
        len(data_collections.all_people[show_index].provided_services),
        "Service Revenue",
    )
    """
    initialize_new_graph(
        lambda: [c.balance for c in allCountries], COUNTRY_COUNT, "Country Balance"
    )
    initialize_new_graph(
        lambda: [c.inflation for c in allCountries], COUNTRY_COUNT, "Country Inflation"
    )"""
    graph_utils.initialize_new_graph(
        lambda: [c.value for c in data_collections.all_currencies],
        constants.COUNTRY_COUNT,
        "Currency Value",
    )

    agent = data_collections.all_people[0]

    while True:
        agent.decide_action()
        agent.apply_action()

        update_utils.update(day)
        update_utils.after_update()

        agent.store_reward()
        if agent.should_update():
            agent.update_policy()

        # Visualizing
        if config.VISUALIZE_GRAPHS:
            graph_utils.update_graphs(day)

        # IO Functions
        io_utils.check_keyboard()

        # Printing
        if day % 50 == 0:
            print("Day: ", day, " Balance: ", data_collections.all_people[0].balance)

        # Do finishing simulation operations
        if (day + 1) % constants.MAX_DAY == 0:
            graph_utils.close_graphs()
            print(f"AI balance: {data_collections.all_people[0].balance}")
            break

        day += 1


print("Starting simulation...")
i = 0
while True:
    episode(i)
    print(f"Episode {i} finished")

    data_collections.all_people[0].save()
    print("Network data saved")

    io_utils.write_data_to_file()
    print("Data written to files")

    i += 1
    read_from_file = True
