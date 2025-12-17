import random
import constants
from enums import ServiceConsumerType
from person_ai_class import PersonAI
from country_class import Country
from person_class import Person
from currency_class import Currency


class Service(object):
    """
    Represents a service offered in the economic simulation.

    A service is sold by a seller, originates from a country, and is priced in the country's currency.
    Its price, demand, and supply evolve over time based on market interactions and consumer preferences.

    Class Attributes:
        services_bought_total (int): Total number of services bought across the simulation.
        service_id (int): Auto-incrementing identifier for services.

    Attributes:
        id (int): Unique identifier of the service.
        name (str): Name of the service.
        base_price (float): Initial base price of the service.
        price (float): Current market price.
        previous_price (float): Price in the previous simulation step.
        supply (int): Current available supply.
        demand (int): Current demand count.
        new_supply (int): Amount of newly generated supply per step.
        cost_of_new_supply (float): Cost to produce new supply.
        origin_country (Country): Country where the service originates.
        seller (Person): Seller providing the service.
        service_type (ServiceType): Category/type of the service.
        currency (Currency): Currency used for transactions.
        age_preference (dict[int, float]): Preference weights by age group.
        gender_preference (dict[int, float]): Preference weights by gender.
        revenue (float): Revenue generated in the current step.
        previous_revenue (float): Revenue from the previous step.
        bought_recently_count (int): Number of recent purchases.
        can_buy_count (int): Number of agents able to buy this service.
        supply_before_sales (int): Supply level before sales occur.
    """

    # Class attributes
    services_bought_total: int = 0
    service_id: int = 0

    # Instance attributes
    id: int
    name: str
    base_price: float
    price: float
    previous_price: float
    demand: int
    supply: int
    new_supply: int
    cost_of_new_supply: float
    origin_country: Country
    seller: Person
    currency: Currency
    consumer_type: ServiceConsumerType
    age_preference: dict[int, float]
    gender_preference: dict[int, float]
    revenue: float
    previous_revenue: float
    bought_recently_count: int
    can_buy_count: int
    supply_before_sales: int

    def __init__(
        self,
        name: str,
        base_price: float,
        initial_supply: int,
        seller: Person,
        consumer_type: ServiceConsumerType,
    ) -> None:
        self.id = Service.service_id
        Service.service_id += 1
        self.name = name
        self.base_price = base_price
        self.supply = initial_supply
        self.demand = 0

        self.origin_country = seller.country
        self.origin_country.country_services.append(self)
        self.currency = self.origin_country.currency

        self.seller = seller
        self.seller.person_services.append(self)

        self.consumer_type = consumer_type

        self.price = self.base_price
        self.previous_price = self.base_price

        # self.currency.demand += self.price

        self.new_supply = random.randint(1, 20)
        self.cost_of_new_supply = random.uniform(
            self.price - 5, self.price + 5
        )  # TODO: Need more complex algorithm to compute this.

        self.age_preference = {}
        for i in range(4):
            self.age_preference[i] = random.random()

        self.gender_preference = {}
        for i in range(2):
            self.gender_preference[i] = random.random()

        self.previous_revenue = 0
        self.revenue = 0
        self.bought_recently_count = 0
        self.can_buy_count = 0

        self.supply_before_sales = self.supply

    def adjust_supply(self) -> None:
        """Adjust supply based on current supply and demand levels."""

        # If demand is overwhelming, invest to increase manufacturing
        if self.supply * 2 < self.demand:
            self.invest()
        if self.supply < self.demand:
            self.supply += self.new_supply

    def invest(self):
        """Invest capital to increase future manufacturing capacity."""
        # TODO : MONEY DISAPPEARS HERE, FIND A SOLUTION
        investment_cost = self.new_supply * self.price
        if self.seller.balance > investment_cost:
            self.seller.balance -= investment_cost
            self.new_supply *= 11 / 10

    def adjust_price(self):
        """Adjust price based on current supply and demand levels."""
        if isinstance(self.seller, PersonAI):
            return

        # Not always
        if random.random() < 0.1:
            self.previous_price = self.price
            if self.demand == 0:
                self.price *= 0.99
            elif self.supply > 0:
                self.price = self.base_price * (self.demand / self.supply)

    def sale_operations(self):
        """Consequences of transaction"""
        self.seller.balance += self.price
        self.currency.demand += self.price

        self.origin_country.exports += self.price
        self.origin_country.gdp += self.price

        self.supply -= 1
        self.revenue += self.price

        self.services_bought_total += 1
        self.bought_recently_count += 1
