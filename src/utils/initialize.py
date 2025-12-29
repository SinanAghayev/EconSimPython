import os
import random
import shutil

import src.data_types.constants as constants
import src.data_types.config as config
import src.data_types.data_collections as data_collections
import src.data_types.enums as enums

from src.data_types.currency_class import Currency
from src.data_types.country_class import Country
from src.data_types.service_class import Service
from src.data_types.person_class import Person
from src.data_types.person_ai_class import PersonAI

import src.utils.update_utils as update_utils
import src.utils.io_utils as io_utils


def start():
    data_collections.all_currencies.clear()
    data_collections.all_countries.clear()
    data_collections.all_people.clear()
    data_collections.all_services.clear()

    init_currencies()
    init_countries()
    init_people()
    init_services()
    update_utils.evaluate_all_services()
    set_taxes()

    if isinstance(data_collections.all_people[0], PersonAI):
        data_collections.all_people[0].initVariables()


def init_currencies():
    if config.READ_FROM_FILE:
        io_utils.read_currencies_from_file()
    else:
        for i in range(constants.COUNTRY_COUNT):
            currency = Currency("Currency_" + str(i))
            data_collections.all_currencies.append(currency)

    # Set exchange rates all to 1
    for i in range(constants.COUNTRY_COUNT):
        for j in range(constants.COUNTRY_COUNT):
            data_collections.all_currencies[i].exchange_rate[
                data_collections.all_currencies[j]
            ] = 1


def init_countries():
    if config.READ_FROM_FILE:
        io_utils.read_countries_from_file()
        return

    for i in range(constants.COUNTRY_COUNT):
        prosperity = random.randint(1, constants.MAX_PROSPERITY)

        country = Country(
            "Country_" + str(i), data_collections.all_currencies[i], prosperity
        )
        data_collections.all_countries.append(country)


def init_services():
    Service.service_id = 0

    if config.READ_FROM_FILE:
        io_utils.read_services_from_file()
        return

    for i in range(constants.SERVICE_COUNT):
        rnd = random.randint(1, constants.PEOPLE_COUNT - 1)
        if i < 5:  # First x services are given to AI
            rnd = 0

        price = random.uniform(1, constants.CEIL_PRICE)
        initial_supply = 10
        seller = data_collections.all_people[rnd]

        service = Service(
            "Service_" + str(i),
            price,
            initial_supply,
            seller,
            random.choice(list(enums.ServiceConsumerType)),
        )
        data_collections.all_services.append(service)


def init_people():
    if config.READ_FROM_FILE:
        io_utils.read_people_from_file()
        return

    if os.path.exists("networks"):
        shutil.rmtree("networks")
    os.mkdir("networks")

    for i in range(constants.PEOPLE_COUNT):
        age_group = random.choice(list(enums.AgeGroup))
        gender = random.choice(list(enums.Gender))
        country = data_collections.all_countries[
            random.randint(0, constants.COUNTRY_COUNT - 1)
        ]

        if i == 0 and config.AI_PERSON_EXISTS:
            person = PersonAI("Person_" + str(i), age_group, gender, country)
        else:
            person = Person("Person_" + str(i), age_group, gender, country)
        data_collections.all_people.append(person)

        # First "demand or not", second "time of demand"
        person.service_demand_state = [(False, 0)] * constants.SERVICE_COUNT


def set_taxes():
    for i in range(constants.COUNTRY_COUNT):
        data_collections.all_countries[i].set_taxes()
