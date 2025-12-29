import csv
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
    with open("data/currencies.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            currency = Currency(row["name"])
            data_collections.all_currencies.append(currency)


def read_countries_from_file():
    with open("data/countries.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            prosperity = random.randint(1, constants.MAX_PROSPERITY)
            currency = data_collections.all_currencies[int(row["currency_index"])]

            country = Country(row["name"], currency, prosperity)
            data_collections.all_countries.append(country)


def read_people_from_file():
    with open("data/people.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            age_group = enums.AgeGroup[row["age_group"]]
            gender = enums.Gender[row["gender"]]
            country = data_collections.all_countries[int(row["country_index"])]

            if i == 0 and config.AI_PERSON_EXISTS:
                person = PersonAI(row["name"], age_group, gender, country)
            else:
                person = Person(row["name"], age_group, gender, country)

            person.demandedServices = [(0, 0)] * constants.SERVICE_COUNT
            data_collections.all_people.append(person)


def read_services_from_file():
    with open("data/services.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            price = random.uniform(1, constants.CEIL_PRICE)
            seller = data_collections.all_people[int(row["seller_index"])]
            consumer_type = enums.ServiceConsumerType[row["consumer_type"]]

            service = Service(
                row["name"],
                price,
                initial_supply=10,
                seller=seller,
                customer_type=consumer_type,
            )
            data_collections.all_services.append(service)


def write_data_to_file():
    with open("data/currencies.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name"])
        for currency in data_collections.all_currencies:
            writer.writerow([currency.name])

    with open("data/countries.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "currency_index"])
        for country in data_collections.all_countries:
            writer.writerow(
                [
                    country.name,
                    data_collections.all_currencies.index(country.currency),
                ]
            )

    with open("data/people.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "age_group", "gender", "country_index"])
        for person in data_collections.all_people:
            writer.writerow(
                [
                    person.name,
                    person.age_group.name,
                    person.gender.name,
                    data_collections.all_countries.index(person.country),
                ]
            )

    with open("data/services.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "seller_index", "consumer_type"])
        for service in data_collections.all_services:
            writer.writerow(
                [
                    service.name,
                    data_collections.all_people.index(service.seller),
                    service.consumer_type.name,
                ]
            )
