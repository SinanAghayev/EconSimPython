import random
from enums import AgeGroup, Gender
from country_class import Country
from service_class import Service
import data_collections


class Person(object):
    """
    Represents an individual participating in the economic simulation.

    Attributes:
        name (str): Name of the person.
        age_group (AgeGroup): Age group of the person.
        gender (Gender): Gender of the person.
        country (Country): Country the person belongs to.
        balance (float): Current monetary balance.
        previous_balance (float): Balance from the previous step.
        save_urge (float): Tendency to save money (0.0–0.8).
        service_preferences (dict[Service, float]): Preference weights for services.
        service_demand_state (dict[int, tuple[bool, int]]):
            Per-service demand state for demanded services
            Each value is (is_demanding, wait_days).
        provided_services (list[Service]): Services provided by this person.
        bought_services_count (int): Number of services bought so far.
    """

    name: str
    age_group: AgeGroup
    gender: Gender
    country: Country
    balance: float
    previous_balance: float
    save_urge: float
    service_preferences: dict[Service, float]
    service_demand_state: dict[int, tuple[bool, int]]
    provided_services: list
    bought_services_count: int

    def __init__(
        self, name: str, age_group: AgeGroup, gender: Gender, country: Country
    ) -> None:
        self.name = name
        self.age_group = age_group
        self.gender = gender
        self.country = country

        self.balance = (
            self.age_group.balance_multiplier
            * self.country.prosperity
            * random.uniform(1, 100)
        )
        self.previous_balance = self.balance

        self.country.currency.supply += self.balance
        self.country.currency.demand += self.balance
        self.save_urge = random.uniform(0, 0.8)

        self.service_preferences = {}
        self.service_demand_state = []

        self.provided_services = []
        self.bought_services_count = 0

    def person_next(self):
        """Do person actions"""
        self.try_buying()

        self.update_save_urge()
        self.previous_balance = self.balance

    def evaluate_services(self):
        """Updates preferences and demands."""
        for service in data_collections.all_services:
            preference = self.compute_service_preference(service)
            self.service_preferences[service] = preference

            price_in_local_currency = (
                service.price * service.currency.exchange_rate[self.country.currency]
            )
            self.update_demand_state(service, preference, price_in_local_currency)

    def compute_service_preference(self, service: Service) -> float:
        if service.seller == self:
            return -1.0

        affordability_penalty = (
            service.price / self.balance if self.balance > 0 else 1.0
        )

        discount_factor = (
            (service.base_price - service.price) / service.price
            if service.price > 0
            else 0.0
        )

        return (
            0.2 * service.age_preference[self.age_group]
            + 0.2 * service.gender_preference[self.gender]
            + 0.3 * random.random()
            - 0.2 * affordability_penalty
            + 0.3 * discount_factor
        )

    def update_demand_state(
        self,
        service: Service,
        preference: float,
        price_in_local: float,
    ):
        """
            Updates the demand state for given service
            Services that are cheap and have high preference and are not already demanded
        Args:
            service (Service): Service to update state
            preference (float): Preference of the service
            price_in_local (float): Price of the service on local currency
        """

        is_demanding, wait_days = self.service_demand_state[service.id]

        # If preferred the service for 3 consecutive days, then it is demanded.
        if (
            not is_demanding
            and preference > self.save_urge
            and price_in_local < self.balance
            and wait_days > 3
        ):
            service.demand += 1
            self.service_demand_state[service.id] = (True, 0)

        elif (
            preference < self.save_urge  # Would rather save money than buy
            or price_in_local > self.balance  # Insufficient funds
        ) and is_demanding:
            service.demand -= 1
            self.service_demand_state[service.id] = (False, 0)

        elif not is_demanding:
            self.service_demand_state[service.id] = (False, wait_days + 1)

    def update_save_urge(self):
        if random.random() < 0.05:
            self.save_urge *= self.prevBalance / self.balance
        self.saveUrge = min(self.saveUrge, 0.8)

    def try_buying(self):
        bought = []
        for service in self.service_preferences.keys():
            if service.supply < 1:
                continue
            if self.service_preferences[service] < self.save_urge:
                continue
            if random.random() < 0.1:
                continue

            if self.buy(service):
                bought.append(service)

        for service in bought:
            self.service_preferences[service] *= self.service_preferences[service]

    def buy(self, service: Service) -> bool:
        """
        Attempts to purchase a service.

        Applies currency conversion and import taxes, checks affordability,
        updates balances, demand, and economic indicators, and triggers the
        service sale operation.

        Returns:
            bool: True if the purchase succeeds, False if insufficient funds.
        """
        price_in_local_currency = (
            service.price * service.currency.exchange_rate[self.country.currency]
        )
        import_tax = self.country.import_taxes[service]
        tax_included_local_price = price_in_local_currency * (1 + import_tax)

        if tax_included_local_price > self.balance:
            return False

        if tax_included_local_price < 0:
            print(
                "NEGATIVE PRICE",
                price_in_local_currency,
                self.country.import_taxes[service],
            )
            return False

        service.can_buy_count += 1
        if self.country != service.origin_country:
            self.country.gdp -= price_in_local_currency

        self.balance -= tax_included_local_price
        self.bought_services_count += 1

        self.country.balance += price_in_local_currency * import_tax
        self.country.currency.demand -= price_in_local_currency
        self.country.exports -= price_in_local_currency

        is_demanding, _ = self.service_demand_state[service.id]
        if is_demanding:
            service.demand -= 1
            self.service_demand_state[service.id] = (False, 0)

        service.sale_operations()
        return True
