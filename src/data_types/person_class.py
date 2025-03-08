import random
from .lists import *


class Person(object):
    def __init__(self, name, age, gender, country) -> None:
        self.name = name
        self.age = age  # groups, 0 child 1 teen 2 adult 3 elder
        self.gender = gender  # 0 w, 1 m
        self.country = country

        self.balance = (self.age + 1) * self.country.prosperity * random.uniform(1, 100)
        self.prevBalance = self.balance

        self.country.currency.supply += self.balance
        self.country.currency.demand += self.balance
        self.saveUrge = random.uniform(0, 0.8)

        self.prefService = {}
        self.demandedServices = []

        self.personServices = []
        self.boughtServices = 0

    def personNext(self):
        self.tryBuying()

        self.setSaveUrge()
        self.prevBalance = self.balance

    def setPreferences(self):
        for service in allServices:
            price = 1 if (service.price == 0) else service.price

            servicePref = (
                0.2 * service.agePref[self.age]
                + 0.2 * service.genderPref[self.gender]
                + 0.3 * random.random()
                - 0.2 * (service.price / self.balance)
                + 0.3 * (service.basePrice - price) / price
            )

            if service.seller == self:
                servicePref = -1
            self.prefService[service] = servicePref

            # Demand services that are cheap and have high preference and are not already demanded
            priceInLocal = (
                service.price * service.currency.exchangeRate[self.country.currency]
            )
            if (
                not self.demandedServices[service.id][0]
                and servicePref > self.saveUrge
                and priceInLocal < self.balance
                and self.demandedServices[service.id][1] > 3
            ):
                service.demand += 1
                self.demandedServices[service.id] = (True, 0)
            elif (
                servicePref < self.saveUrge or priceInLocal > self.balance
            ) and self.demandedServices[service.id][0]:
                service.demand -= 1
                self.demandedServices[service.id] = (False, 0)
            elif not self.demandedServices[service.id][0]:
                self.demandedServices[service.id] = (
                    False,
                    self.demandedServices[service.id][1] + 1,
                )

    def setSaveUrge(self):
        if random.random() < 0.1:
            self.saveUrge *= self.prevBalance / self.balance
        self.saveUrge = min(self.saveUrge, 0.8)

    def tryBuying(self):
        bought = []
        for service in self.prefService.keys():
            if service.supply < 1:
                continue
            if self.prefService[service] < self.saveUrge:
                continue
            if random.random() < 0.1:
                continue

            if self.buy(service):
                bought.append(service)

        for s in bought:
            self.prefService[s] *= self.prefService[s]

    def buy(self, service):
        priceInLocal = (
            service.price * service.currency.exchangeRate[self.country.currency]
        )
        if priceInLocal * (1 + self.country.importTax[service]) > self.balance:
            return False
        service.can_buy_count += 1
        if self.country != service.originCountry:
            self.country.gdp -= priceInLocal

        if priceInLocal * (1 + self.country.importTax[service]) < 0:
            print("NEGATIVE PRICE", priceInLocal, self.country.importTax[service])

        self.balance -= priceInLocal * (1 + self.country.importTax[service])
        self.country.balance += priceInLocal * self.country.importTax[service]
        self.country.currency.demand -= priceInLocal
        self.country.exports -= 1
        self.boughtServices += 1

        if self.demandedServices[service.id][0]:
            service.demand -= 1
            self.demandedServices[service.id] = (False, 0)
        service.buyThis()

        return True
