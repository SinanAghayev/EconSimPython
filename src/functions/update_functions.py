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

    first_person = data_collections.all_people[0]
    if isinstance(first_person, PersonAI):
        first_person.decide_action()
        first_person.apply_action()

    for service in data_collections.all_services:
        service.previous_revenue = service.revenue
        service.revenue = 0

    person_actions()
    country_actions()

    if day % constants.INTERVAL == 0:
        calculate_inflation()
        currency_actions()
        service_actions()
    if isinstance(first_person, PersonAI):
        first_person.store_reward()
    day += 1


def evaluate_all_services():
    for person in data_collections.all_people:
        person.evaluate_services()


def set_exchange_rates():
    for i in range(constants.COUNTRY_COUNT):
        currency = data_collections.all_currencies[i]
        for j in range(constants.COUNTRY_COUNT):
            other_currency = data_collections.all_currencies[j]

            rate = currency.value / other_currency.value
            currency.exchangeRate[other_currency] = rate


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
        service.adjust_price()
        service.cost_of_new_supply = random.uniform(
            max(service.price - 5, 1), service.price + 5
        )
        service.price = min(max(service.price, 1), constants.MAX_PRICE)
        if isinstance(service.seller, PersonAI):
            continue
        service.adjustSupply()


def currency_actions():
    for country in data_collections.all_countries:
        country.add_supply_to_currency()


def after_update():
    for service in data_collections.all_services:
        service.bought_recently_count = 0
        service.can_buy_count = 0
