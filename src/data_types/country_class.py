import random
import src.data_types.constants as constants
import src.data_types.data_collections as data_collections
from src.data_types.currency_class import Currency
from src.data_types.service_class import Service


class Country(object):
    """
    Represents a country in the economic simulation.

    Attributes:
        name (str): Name of the country.
        currency (Currency): Currency used by the country.
        prosperity (int): Value between 1 and MAX_PROSPERITY.
        balance (float): Monetary balance in country's currency.
        gdp (float): Gross domestic product.
        inflation (float): Inflation rate.
        exports (float): Total exports, sum of transactions amount * price, imports are substracted.
        import_taxes (dict[Service, float]): Mapping of service -> tax percentage.
        country_services (list): Services originated from this country.
    """

    name: str
    currency: Currency
    prosperity: int
    balance: float
    gdp: float
    inflation: float
    exports: float
    import_taxes: dict[Service, float]
    country_services: list

    def __init__(self, name: str, currency: Currency, prosperity: int) -> None:
        self.name = name
        self.currency = currency
        self.prosperity = prosperity
        self.balance = self.prosperity * random.uniform(100, 10000)

        self.gdp = 0
        self.inflation = 0
        self.exports = 0

        self.currency.supply += self.balance
        self.currency.demand += self.balance

        self.import_taxes = {}
        self.country_services = []

    def country_next(self) -> None:
        """Do country actions"""
        self.try_buying()

    def try_buying(self) -> None:
        """Find services that can be bought and try buying them"""
        for service in data_collections.all_services:
            if service.service_type == constants.TargetType.REGULAR:
                continue
            elif service.supply < 1:
                continue

            self.buy(service)

    def buy(self, service: Service):
        """Buy the given service if have the sufficient funds

        Args:
            service (Service): Service to buy
        """
        price_in_local = service.price * service.currency.exchange_rate[self.currency]
        if price_in_local > self.balance:
            return
        if self != service.origin_country:
            self.gdp -= price_in_local

        self.balance -= price_in_local
        self.currency.demand -= price_in_local

        service.sale_operations()

    def add_supply_to_currency(self):
        """Print new money"""
        self.balance += self.currency.supply / 10
        self.currency.supply += self.currency.supply / 10
        self.currency.adjust_value()

    def set_taxes(self):
        """Sets the taxes randomly"""
        for i in range(constants.SERVICE_COUNT):
            self.importTax[data_collections.all_services[i]] = random.uniform(0, 0.3)

    def calculate_inflation(self):
        """
        Calculates the inflation using simple Customer Price Index (CPI) method
        CPI = Sum of price of all services originated in this country
        # TODO: This is wrong, not all sold items are originated in this country.
        """

        previous_CPI = 0
        previous_CPI = 0
        for service in self.country_services:
            current_CPI += service.price
            previous_CPI += service.previousPrice

        if previous_CPI == 0:
            self.inflation = 0
            return

        self.inflation = ((previous_CPI - previous_CPI) / previous_CPI) * 100
