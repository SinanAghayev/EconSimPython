import sys
import os
import random
import shutil
import time
import tkinter as tk

import keyboard
from data_types.constants import *
from data_types.lists import *
from data_types.currency_class import Currency
from data_types.country_class import Country
from data_types.service_class import Service
from data_types.person_class import Person
from data_types.person_ai_class import PersonAI

from graph import RealTimeGraph

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

day = 0

def start():
    initCurrencies()
    initCountries()
    initPeople()
    initServices()
    setAllPreferences()
    setTaxes()
    
    if allPeople[0].__class__ == PersonAI:
        allPeople[0].initNetworks()


def update():
    nextIteration()
    if day % 100 == 0:
        print("Day: ", day, " Balance: ", allPeople[0].balance)


def nextIteration():
    setExchangeRates()
    peopleActions()
    countryActions()

    global day
    if day % INTERVAL == 0:
        calculateInflation()
        currencyActions()
        serviceActions()
        setAllPreferences()
    day += 1


def calculateInflation():
    for country in allCountries:
        country.calculateInflation()


def serviceActions():
    for service in allServices:
        service.adjustPrice()
        service.price = min(service.price, MAX_PRICE)
        if service.seller is allPeople[0]:
            continue
        service.adjustSupply()


def currencyActions():
    for country in allCountries:
        country.addSupplyToCurrency()


def countryActions():
    for country in allCountries:
        country.countryNext()


def peopleActions():
    for person in allPeople:
        person.personNext()
        person.balance += 1


def setExchangeRates():
    for i in range(COUNTRY_COUNT):
        for j in range(COUNTRY_COUNT):
            rate = allCurrencies[i].value / allCurrencies[j].value
            allCurrencies[i].exchangeRate[allCurrencies[j]] = rate


def setAllPreferences():
    for person in allPeople:
        person.setPreferences()


def initCurrencies():
    allCurrencies.clear()
    if read_from_file:
        with open("data/currencies.txt", "r") as f:
            for line in f:
                arg = line.strip().split()
                currency = Currency(arg[0])
                allCurrencies.append(currency)
    
    for i in range(COUNTRY_COUNT):
        currency = Currency("Currency_" + str(i))
        allCurrencies.append(currency)
    for i in range(COUNTRY_COUNT):
        for j in range(COUNTRY_COUNT):
            allCurrencies[i].exchangeRate[allCurrencies[j]] = 1

def initCountries():
    allCountries.clear()
    if read_from_file:
        with open("data/countries.txt", "r") as f:
            for line in f:
                arg = line.strip().split()
                country = Country(arg[0], allCurrencies[int(arg[1])], int(arg[2]))
                allCountries.append(country)
    
    for i in range(COUNTRY_COUNT):
        prosperity = random.randint(1, MAX_PROSPERITY)
        country = Country("Country_" + str(i), allCurrencies[i], prosperity)
        allCountries.append(country)


def initServices():
    Service.service_id = 0
    allServices.clear()
    if read_from_file:
        with open("data/services.txt", "r") as f:
            for line in f:
                arg = line.strip().split()
                price = float(arg[1])
                initialSupply = int(arg[2])
                service = Service(
                    arg[0],
                    price,
                    initialSupply,
                    allPeople[int(arg[3])],
                    int(arg[4]),
                )
                allServices.append(service)
        return
    Service.service_id = 0
    for i in range(SERVICE_COUNT):
        price = random.uniform(1, CEIL_PRICE)
        initialSupply = 10

        rnd = random.randint(0, PEOPLE_COUNT - 1)
        service = Service(
            "Service_" + str(i),
            price,
            initialSupply,
            allPeople[rnd],
            random.randint(0, 2),
        )
        allServices.append(service)


def initPeople():
    allPeople.clear()
    if read_from_file:
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
        person.demandedServices = [(0, 0)] * SERVICE_COUNT


def setTaxes():
    for i in range(COUNTRY_COUNT):
        allCountries[i].setTaxes()


def checkKeyboard():
    global wait
    if keyboard.is_pressed("A"):
        wait = False
    if keyboard.is_pressed("S"):
        wait = True

    if wait:
        time.sleep(0.1)

show_index = 0

def episode(i):
    if i != 0:
        global read_from_file
        read_from_file = True
    start()
    print(f"Episode {i} started")
    root = tk.Tk()
    app = RealTimeGraph(root, PEOPLE_COUNT, "People Balance")

    serv_root = tk.Tk()
    serv_app = RealTimeGraph(serv_root, len(allPeople[show_index].personServices), "Service Price")

    serv_dem_root = tk.Tk()
    serv_dem_app = RealTimeGraph(serv_dem_root, len(allPeople[show_index].personServices), "Service Demand")

    serv_sup_root = tk.Tk()
    serv_sup_app = RealTimeGraph(serv_sup_root, len(allPeople[show_index].personServices), "Service Supply")

    global wait
    wait = False
    while True:
        global day
        
        update()
        temp = [person.balance for person in allPeople]
        app.update_graph(temp)
        serv_app.update_graph([serv.price for serv in allPeople[show_index].personServices])
        serv_dem_app.update_graph([serv.demand for serv in allPeople[show_index].personServices])
        serv_sup_app.update_graph([serv.supply for serv in allPeople[show_index].personServices])
        root.update()
        serv_root.update()
        serv_dem_root.update()
        serv_sup_root.update()
        
        if (day + 1) % 50 == 0 and allPeople[0].__class__ == PersonAI:
            allPeople[0].gamma *= 0.9
        if (day + 1) % 100 == 0 and allPeople[0].__class__ == PersonAI:
            allPeople[0].save()
        if (day + 1) % 250 == 0:
            root.destroy()
            serv_root.destroy()
            serv_dem_root.destroy()
            serv_sup_root.destroy()
            day = 0
            print(f"AI balance: {allPeople[0].balance}")
            break

        checkKeyboard()

def write_data():
    with open("data/people.txt", "w") as f:
        for person in allPeople:
            f.write(f"{person.name} {person.age} {person.gender} {allCountries.index(person.country)}\n")
    with open("data/countries.txt", "w") as f:
        for country in allCountries:
            f.write(f"{country.name} {allCurrencies.index(country.currency)} {country.prosperity}\n")
    with open("data/services.txt", "w") as f:
        for service in allServices:
            f.write(f"{service.name} {service.price} {int(service.supply)} {allPeople.index(service.seller)} {service.serviceType}\n")
    with open("data/currencies.txt", "w") as f:
        for currency in allCurrencies:
            f.write(f"{currency.name}\n")

print("Starting simulation...")
i = 0
while True:
    episode(i)
    print(f"Episode {i} finished")
    write_data()
    print("Data written to files")
    i += 1

