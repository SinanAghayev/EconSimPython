import random
import keyboard
import time

import src.data_types.config as config
import src.data_types.data_collections as data_collections
import src.data_types.constants as constants
import src.data_types.enums as enums

from src.data_types.currency_class import Currency
from src.data_types.country_class import Country
from src.data_types.service_class import Service
from src.data_types.person_class import Person
from src.data_types.person_ai_class import PersonAI


def check_keyboard():
    if keyboard.is_pressed("A"):
        config.WAIT_FOR_INPUT = False
    if keyboard.is_pressed("S"):
        config.WAIT_FOR_INPUT = True

    if keyboard.is_pressed("V"):
        config.VISUALIZE_GRAPHS = True
    if keyboard.is_pressed("B"):
        config.VISUALIZE_GRAPHS = False

    if config.WAIT_FOR_INPUT:
        time.sleep(1)


def read_currencies_from_file():
    with open("data/currencies.txt", "r") as f:
        for line in f:
            arg = line.strip().split()
            currency_name = arg[0]
            currency = Currency(currency_name)
            data_collections.all_currencies.append(currency)


def read_countries_from_file():
    with open("data/countries.txt", "r") as f:
        for line in f:
            arg = line.strip().split()
            prosperity = random.randint(1, constants.MAX_PROSPERITY)

            country_name = arg[0]
            country_currency = data_collections.all_currencies[int(arg[1])]
            country = Country(country_name, country_currency, prosperity)
            data_collections.all_countries.append(country)


def read_services_from_file():
    with open("data/services.txt", "r") as f:
        for line in f:
            arg = line.strip().split()

            service_name = arg[0]
            price = random.uniform(1, constants.CEIL_PRICE)
            initial_supply = 10
            customer_type = enums.ServiceConsumerType[arg[2]]
            seller = data_collections.all_people[int(arg[1])]

            service = Service(
                service_name,
                price,
                initial_supply,
                seller,
                customer_type,
            )
            data_collections.all_services.append(service)


def read_people_from_file():
    with open("data/people.txt", "r") as f:
        for i, line in enumerate(f):
            arg = line.strip().split()
            name = arg[0]
            age_group = enums.AgeGroup[arg[1]]
            gender = enums.Gender[arg[2]]
            country = data_collections.all_countries[int(arg[3])]
            if i == 0 and config.AI_PERSON_EXISTS:
                person = PersonAI(name, age_group, gender, country)
            else:
                person = Person(name, age_group, gender, country)
            data_collections.all_people.append(person)

            person.demandedServices = [(0, 0)] * constants.SERVICE_COUNT


def write_data_to_file():
    with open("data/people.txt", "w") as f:
        for person in data_collections.all_people:
            f.write(
                f"{person.name} {person.age_group.name} {person.gender.name} {data_collections.all_countries.index(person.country)}\n"
            )
    with open("data/countries.txt", "w") as f:
        for country in data_collections.all_countries:
            f.write(
                f"{country.name} {data_collections.all_currencies.index(country.currency)}\n"
            )
    with open("data/services.txt", "w") as f:
        for service in data_collections.all_services:
            f.write(
                f"{service.name} {data_collections.all_people.index(service.seller)} {service.consumer_type.name}\n"
            )
    with open("data/currencies.txt", "w") as f:
        for currency in data_collections.all_currencies:
            f.write(f"{currency.name}\n")
