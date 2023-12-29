import random
import time
import tkinter as tk

import keyboard
from constants import *
from lists import *
from currencyClass import Currency
from countryClass import Country
from serviceClass import Service
from personClass import Person
from personAIClass import PersonAI

from test import RealTimeGraph

day = 0


def start():
    initCurrencies()
    initCountries()
    initPeople()
    initServices()
    setAllPreferences()
    setTaxes()


def update():
    nextIteration()


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
        if service.seller is allPeople[0]:
            continue
        service.addSupply()
        service.adjustPrice()


def currencyActions():
    for country in allCountries:
        country.addSupplyToCurrency()


def countryActions():
    for country in allCountries:
        country.countryNext()


def peopleActions():
    for person in allPeople:
        person.personNext()


def setExchangeRates():
    for i in range(COUNTRY_COUNT):
        for j in range(COUNTRY_COUNT):
            rate = allCurrencies[i].value / allCurrencies[j].value
            allCurrencies[i].exchangeRate[allCurrencies[j]] = rate


def setAllPreferences():
    for person in allPeople:
        person.setPreferences()


def initCurrencies():
    for i in range(COUNTRY_COUNT):
        currency = Currency("Currency " + str(i))
        allCurrencies.append(currency)
    for i in range(COUNTRY_COUNT):
        for j in range(COUNTRY_COUNT):
            allCurrencies[i].exchangeRate[allCurrencies[j]] = 1


def initCountries():
    for i in range(COUNTRY_COUNT):
        prosperity = random.randint(1, MAX_PROSPERITY)
        country = Country("Country " + str(i), allCurrencies[i], prosperity)
        allCountries.append(country)


def initServices():
    for i in range(SERVICE_COUNT):
        price = random.uniform(1, CEIL_PRICE)
        initialSupply = random.randint(1, 100)

        rnd = random.randint(0, PEOPLE_COUNT - 1)
        service = Service(
            "Service " + str(i),
            price,
            initialSupply,
            allPeople[rnd],
            random.randint(0, 2),
        )
        allServices.append(service)


def initPeople():
    for i in range(PEOPLE_COUNT):
        age = random.randint(0, 3)
        gender = random.randint(0, 1)
        country = random.randint(0, COUNTRY_COUNT - 1)

        if i == 0:
            person = PersonAI("Person " + str(i), age, gender, allCountries[country])
            person.initNetworks()
        else:
            person = Person("Person " + str(i), age, gender, allCountries[country])
        allPeople.append(person)


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


start()
root = tk.Tk()
app = RealTimeGraph(root, PEOPLE_COUNT)

wait = False
while True:
    update()
    temp = [person.balance for person in allPeople]
    app.update_graph(temp)
    root.update()
    checkKeyboard()
