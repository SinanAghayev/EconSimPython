class Currency(object):
    """
    Represents a currency in the economic simulation.

    Attributes:
        name (str): Name of the currency.
        exchange_rate (dict[str, float]): Mapping of currency name to exchange rate.
            One unit of this currency equals *x* units of the target currency.
        demand (float): Total demand for this currency, representing how frequently
            it is used in transactions. Transactions are executed in the seller's currency.
        supply (float): Total supply (existance) of this currency in the simulation.
        value (float): Computed value of the currency, calculated as demand / supply.
    """

    name: str
    exchange_rate: dict[str, float]
    demand: int
    supply: int
    value: float

    def __init__(self, name: str) -> None:
        self.name = name
        self.exchange_rate = {}
        self.demand = 0
        self.supply = 0
        self.value = 0

    def adjust_value(self):
        """Adjusts the value of the currecy depending on demand and supply"""
        self.value = 0 if self.supply == 0 else self.demand / self.supply
