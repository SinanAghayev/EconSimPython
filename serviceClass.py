import random
from constants import *


class Service(object):
    servicesBought = 0

    def __init__(self, name, basePrice, initialSupply, seller, serviceType) -> None:
        self.name = name
        self.basePrice = basePrice
        self.supply = initialSupply
        self.demand = 0

        self.originCountry = seller.country
        self.originCountry.countryServices.append(self)
        self.seller = seller
        self.serviceType = serviceType

        self.price = self.basePrice
        self.previousPrice = self.price

        self.currency = self.originCountry.currency
        self.currency.demand += self.price

        self.newSupply = random.randint(1, 20)
        self.seller.personServices.append(self)

        self.agePref = {}
        for i in range(4):
            self.agePref[i] = random.random()

        self.genderPref = {}
        for i in range(2):
            self.genderPref[i] = random.random()

        self.prevRevenue = 0
        self.revenue = 0

    def addSupply(self):
        # TODO
        if self.supply * 2 < self.demand:
            self.invest()
        if self.supply < self.demand:
            self.supply += self.newSupply

    def invest(self):
        # TODO : MONEY DISAPPEARS HERE, FIND A SOLUTION
        if self.seller.balance > self.newSupply * self.price:
            self.seller.balance -= self.newSupply * self.price
            self.newSupply *= 11 / 10

    def adjustPrice(self):
        if random.random() < 0.1:
            self.previousPrice = self.price
            self.price = self.basePrice * (self.demand / self.supply)
        self.prevRevenue = self.revenue
        self.revenue = 0

    def buyThis(self):
        self.seller.balance += self.price * (1 - self.originCountry.exportTax[self])
        self.originCountry.balance += self.price * self.originCountry.exportTax[self]

        self.currency.demand += self.price

        self.originCountry.exports += 1

        self.originCountry.gdp += self.price
        self.supply -= 1

        self.revenue += self.price
        self.servicesBought += 1
