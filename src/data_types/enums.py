from enum import Enum, auto


# Enum for the type of service
class ServiceConsumerType(Enum):
    GOVERNMENT = auto()
    REGULAR = auto()
    ALL = auto()


class AgeGroup(Enum):
    CHILD = auto()
    TEEN = auto()
    ADULT = auto()
    ELDER = auto()

    @property
    def balance_multiplier(self) -> float:
        return {
            AgeGroup.CHILD: 0.5,
            AgeGroup.TEEN: 0.8,
            AgeGroup.ADULT: 2,
            AgeGroup.ELDER: 3,
        }[self]


class Gender(Enum):
    MALE = auto()
    FEMALE = auto()
