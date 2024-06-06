import random
from lists import *


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

            priceInLocal = service.price * service.currency.exchangeRate[self.country.currency]
            if servicePref > self.saveUrge and priceInLocal < self.balance and self.demandedServices[service.id][0] == 0 and self.demandedServices[service.id][1] > 7:
                service.demand += 1
                self.demandedServices[service.id] = (1, 0)
            elif (servicePref < self.saveUrge or priceInLocal < self.balance) and self.demandedServices[service.id][0]:
                service.demand -= 1
                self.demandedServices[service.id] = (0, 0)
            else:
                self.demandedServices[service.id] = (0, self.demandedServices[service.id][1] + 1)

    def setSaveUrge(self):
        if random.random() < 0.1:
            self.saveUrge *= self.prevBalance / self.balance
        self.saveUrge = min(self.saveUrge, 0.8)

    def tryBuying(self):
        bought = []
        for service in self.prefService.keys():
            if (
                self.prefService[service] > self.saveUrge
                and service.supply > 1
                and random.random() > 0.5
            ):
                if self.buy(service):
                    bought.append(service)
        for s in bought:
            self.prefService[s] *= self.prefService[s]

    def buy(self, service):
        priceInLocal = (
            service.price * service.currency.exchangeRate[self.country.currency]
        )
        if self.balance < priceInLocal * (1 + self.country.importTax[service]):
            return False
        if self.country != service.originCountry:
            self.country.gdp -= priceInLocal

        self.balance -= priceInLocal * (1 + self.country.importTax[service])
        self.country.balance += priceInLocal * self.country.importTax[service]
        self.country.currency.demand -= priceInLocal
        self.country.exports -= 1
        self.boughtServices += 1

        if self.demandedServices[service.id][0]:
            service.demand -= 1
            self.demandedServices[service.id] = (0, 0)
        service.buyThis()
        
        return True
