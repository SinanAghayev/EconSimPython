import random
import keyboard
import time

from data_types.constants import *
from data_types.lists import *

from data_types.currency_class import Currency
from data_types.country_class import Country
from data_types.service_class import Service
from data_types.person_class import Person
from data_types.person_ai_class import PersonAI

def check_keyboard():
    if keyboard.is_pressed("A"):
        keyboard_constants["wait"] = False
    if keyboard.is_pressed("S"):
        keyboard_constants["wait"] = True

    if keyboard.is_pressed("V"):
        keyboard_constants["visualize"] = True
    if keyboard.is_pressed("B"):
        keyboard_constants["visualize"] = False

    # print("Visualize: ", keyboard_constants["visualize"], " Wait: ", keyboard_constants["wait"])
    if keyboard_constants["wait"]:
        time.sleep(1)

def read_currencies_data():
    with open("data/currencies.txt", "r") as f:
        for line in f:
            arg = line.strip().split()
            currency = Currency(arg[0])
            allCurrencies.append(currency)

def read_countries_data():
    with open("data/countries.txt", "r") as f:
        for line in f:
            arg = line.strip().split()
            prosperity = random.randint(1, MAX_PROSPERITY)

            country = Country(arg[0], allCurrencies[int(arg[1])], prosperity)
            allCountries.append(country)

def read_services_data():
    with open("data/services.txt", "r") as f:
            for line in f:
                arg = line.strip().split()

                price = random.uniform(1, CEIL_PRICE)
                initialSupply = 10

                service = Service(
                    arg[0],
                    price,
                    initialSupply,
                    allPeople[int(arg[1])],
                    int(arg[2]),
                )
                allServices.append(service)

def read_people_data():
    with open("data/people.txt", "r") as f:
            for i, line in enumerate(f):
                arg = line.strip().split()
                name = arg[0]
                age = int(arg[1])
                gender = int(arg[2])
                country = allCountries[int(arg[3])]
                if i == 0 and aiPersonExists:
                    person = PersonAI(name, age, gender, country)
                else:
                    person = Person(name, age, gender, country)
                allPeople.append(person)

                person.demandedServices = [(0, 0)] * SERVICE_COUNT

def write_data():
    with open("data/people.txt", "w") as f:
        for person in allPeople:
            f.write(f"{person.name} {person.age} {person.gender} {allCountries.index(person.country)}\n")
    with open("data/countries.txt", "w") as f:
        for country in allCountries:
            f.write(f"{country.name} {allCurrencies.index(country.currency)}\n")
    with open("data/services.txt", "w") as f:
        for service in allServices:
            f.write(f"{service.name} {allPeople.index(service.seller)} {service.serviceType}\n")
    with open("data/currencies.txt", "w") as f:
        for currency in allCurrencies:
            f.write(f"{currency.name}\n")