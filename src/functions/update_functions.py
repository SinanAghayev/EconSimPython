from .initialize import *
from data_types.constants import *


def update(d):
    global day
    day = d

    next_iteration()


def next_iteration():
    global day
    set_all_preferences()
    set_exchange_rates()

    if allPeople[0].__class__ == PersonAI:
        allPeople[0].decide_action()
        allPeople[0].apply_action()

    for service in allServices:
        service.prevRevenue = service.revenue
        service.revenue = 0

    person_actions()
    country_actions()

    if day % INTERVAL == 0:
        calculate_inflation()
        currency_actions()
        service_actions()
    if allPeople[0].__class__ == PersonAI:
        allPeople[0].store_reward()
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
        if person.__class__ == PersonAI:
            continue
        person.personNext()
        person.balance += 1 if person is not allPeople[0] else 0


def country_actions():
    for country in allCountries:
        country.countryNext()


def service_actions():
    for service in allServices:
        service.adjustPrice()
        service.costOfNewSupply = random.uniform(
            max(service.price - 5, 1), service.price + 5
        )
        service.price = min(max(service.price, 1), MAX_PRICE)
        if isinstance(service.seller, PersonAI):
            continue
        service.adjustSupply()


def currency_actions():
    for country in allCountries:
        country.addSupplyToCurrency()


def after_update():
    for service in allServices:
        service.bought_recently_count = 0
        service.can_buy_count = 0
