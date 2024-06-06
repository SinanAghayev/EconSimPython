from .initialize import *
from data_types.constants import *

def update(d):
    global day
    day = d
    
    next_iteration()
    if day % 100 == 0:
        print("Day: ", day, " Balance: ", allPeople[0].balance)

def next_iteration():
    global day
    set_exchange_rates()
    person_actions()
    country_actions()
    
    if day % INTERVAL == 0:
        calculate_inflation()
        currency_actions()
        service_actions()
        set_all_preferences()
    day += 1

def set_exchange_rates():
    for i in range(COUNTRY_COUNT):
        for j in range(COUNTRY_COUNT):
            rate = allCurrencies[i].value / allCurrencies[j].value
            allCurrencies[i].exchangeRate[allCurrencies[j]] = rate
            
def calculate_inflation():
    for country in allCountries:
        country.calculateInflation()
        
def person_actions():
    for person in allPeople:
        person.personNext()
        person.balance += 1
        
def country_actions():
    for country in allCountries:
        country.countryNext()
        
def service_actions():
    for service in allServices:
        service.adjustPrice()
        service.price = min(service.price, MAX_PRICE)
        if service.seller is allPeople[0]:
            continue
        service.adjustSupply()

def currency_actions():
    for country in allCountries:
        country.addSupplyToCurrency()