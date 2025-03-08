import random
from .constants import *
from .lists import *


class Country(object):
    def __init__(self, name, currency, prosperity) -> None:
        self.name = name
        self.currency = currency
        self.prosperity = prosperity
        self.balance = self.prosperity * random.uniform(100, 10000)
        self.gdp = 0
        self.exports = 0
        self.currency.supply += self.balance
        self.currency.demand += self.balance

        self.importTax = {}

        self.countryServices = []
        self.inflation = 0

    def countryNext(self):
        self.tryBuying()

    def tryBuying(self):
        for service in allServices:
            if service.serviceType == TYPE.REGULAR:
                continue
            elif service.supply <= 1:
                continue
            elif random.random() < 0.1:
                continue

            self.buy(service)

    def buy(self, service):
        priceInLocal = service.price * service.currency.exchangeRate[self.currency]
        if priceInLocal > self.balance:
            return
        if self != service.originCountry:
            self.gdp -= priceInLocal

        self.balance -= priceInLocal
        self.currency.demand -= priceInLocal

        service.buyThis()

    def addSupplyToCurrency(self):
        self.currency.adjustValue()
        if self.currency.value > 1:
            self.balance += self.currency.supply / 10
            self.currency.supply += self.currency.supply / 10

    def setTaxes(self):
        for i in range(SERVICE_COUNT):
            self.importTax[allServices[i]] = random.uniform(0, 0.3)

    def calculateInflation(self):
        currCPI = 0
        prevCPI = 0
        for service in self.countryServices:
            currCPI += service.price
            prevCPI += service.previousPrice
        if prevCPI == 0:
            self.inflation = 0
            return
        self.inflation = ((currCPI - prevCPI) / prevCPI) * 100
