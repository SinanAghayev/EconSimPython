import random

import src.data_types.constants as constants
import src.data_types.data_collections as data_collections

from src.data_types.person_ai_class import PersonAI


def update(d):
    global day
    day = d
    next_iteration()


def next_iteration():
    global day
    evaluate_all_services()
    set_exchange_rates()

    for service in data_collections.all_services:
        service.supply_before_sales = service.supply
        service.previous_revenue = service.revenue
        service.revenue = 0

    person_actions()
    country_actions()

    if day % constants.INTERVAL == 0:
        calculate_inflation()
        currency_actions()
        service_actions()


def evaluate_all_services():
    for person in data_collections.all_people:
        person.evaluate_services()


def set_exchange_rates():
    for i in range(constants.COUNTRY_COUNT):
        currency = data_collections.all_currencies[i]
        for j in range(constants.COUNTRY_COUNT):
            other_currency = data_collections.all_currencies[j]

            rate = (
                1
                if other_currency.demand == 0
                else currency.demand / other_currency.demand
            )
            if rate < 0:
                print(
                    "First currency: ", currency.value, currency.demand, currency.supply
                )
                print(
                    "Other currency: ",
                    other_currency.value,
                    other_currency.demand,
                    other_currency.supply,
                )
            currency.exchange_rate[other_currency] = rate


def calculate_inflation():
    for country in data_collections.all_countries:
        country.calculate_inflation()


def person_actions():
    for person in data_collections.all_people:
        if isinstance(person, PersonAI):
            continue
        person.person_next()
        # person.balance += 1


def country_actions():
    for country in data_collections.all_countries:
        country.country_next()


def service_actions():
    for service in data_collections.all_services:
        if isinstance(service.seller, PersonAI):
            continue
        service.adjust_price()
        service.cost_of_new_supply = random.uniform(
            max(service.price - 5, 1), service.price + 5
        )
        service.price = min(max(service.price, 1), constants.MAX_PRICE)
        service.adjust_supply()


def currency_actions():
    for country in data_collections.all_countries:
        country.add_supply_to_currency()


def after_update():
    for service in data_collections.all_services:
        service.bought_recently_count = 0
        service.can_buy_count = 0
