import os
import random
import shutil

from data_types.constants import *
from data_types.lists import *

from data_types.currency_class import Currency
from data_types.country_class import Country
from data_types.service_class import Service
from data_types.person_class import Person
from data_types.person_ai_class import PersonAI

from functions.io_functions import *

def start():
    allCurrencies.clear()
    allCountries.clear()
    allPeople.clear()
    allServices.clear()

    init_currencies()

    for i in range(COUNTRY_COUNT):
        for j in range(COUNTRY_COUNT):
            allCurrencies[i].exchangeRate[allCurrencies[j]] = 1

    init_countries()
    init_people()
    init_services()
    set_all_preferences()
    set_taxes()

    if allPeople[0].__class__ == PersonAI:
        allPeople[0].initNetworks()

def init_currencies():
    if read_from_file:
        read_currencies_data()
        return

    for i in range(COUNTRY_COUNT):
        currency = Currency("Currency_" + str(i))
        allCurrencies.append(currency)


def init_countries():
    if read_from_file:
        read_countries_data()
        return

    for i in range(COUNTRY_COUNT):
        prosperity = random.randint(1, MAX_PROSPERITY)
        country = Country("Country_" + str(i), allCurrencies[i], prosperity)
        allCountries.append(country)


def init_services():
    Service.service_id = 0

    if read_from_file:
        read_services_data()
        return

    Service.service_id = 0
    for i in range(SERVICE_COUNT):
        price = random.uniform(1, CEIL_PRICE)
        initialSupply = 10

        # First service is sold by the first person and the rest are sold by random people
        if i == 0:
            rnd = 0
        else:
            rnd = random.randint(1, PEOPLE_COUNT - 1)

        service = Service(
            "Service_" + str(i),
            price,
            initialSupply,
            allPeople[rnd],
            random.randint(0, 2),
        )
        allServices.append(service)


def init_people():
    if read_from_file:
        read_people_data()
        return

    if os.path.exists("networks"):
        shutil.rmtree("networks")
    os.mkdir("networks")

    for i in range(PEOPLE_COUNT):
        age = random.randint(0, 3)
        gender = random.randint(0, 1)
        country = random.randint(0, COUNTRY_COUNT - 1)

        if i == 0 and aiPersonExists:
            person = PersonAI("Person_" + str(i), age, gender, allCountries[country])
            person.initNetworks()
        else:
            person = Person("Person_" + str(i), age, gender, allCountries[country])
        allPeople.append(person)

        # First demand or not, second time of demand
        person.demandedServices = [(False, 0)] * SERVICE_COUNT

def set_all_preferences():
    for person in allPeople:
        person.setPreferences()

def set_taxes():
    for i in range(COUNTRY_COUNT):
        allCountries[i].setTaxes()