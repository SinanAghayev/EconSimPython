class Currency(object):
    def __init__(self, name) -> None:
        self.currencyName = name
        self.exchangeRate = {}
        self.demand = 1
        self.supply = 1
        self.value = 1

    def adjustValue(self):
        self.value = self.demand / self.supply
