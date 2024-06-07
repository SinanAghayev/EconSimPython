from enum import Enum

# Enum for the type of service
class TYPE(Enum):
    GOVERNMENT = 0
    REGULAR = 1
    ALL = 2

day = 0 # Current day

keyboard_constants = {
    "wait" : False, # If True, the program will wait for the user to press a key before continuing
    "visualize" : False # If True, the program will display the graphs
}

COUNTRY_COUNT = 3 # Number of countries
SERVICE_COUNT = 100 # Number of services
PEOPLE_COUNT = 200 # Number of people
CEIL_PRICE = 500 # Maximum starting price of a service
MAX_PRICE = 100000 # Maximum price of a service
MAX_PROSPERITY = 20 # Maximum prosperity of a country
MAX_DAY = 350 # Maximum number of days the simulation will run for
INTERVAL = 1 # Number of days between each update


aiPersonExists = True # If True, the program will create an AI person. If False, the program will not create an AI person.
read_from_file = False # If True, the program will read from the data files. If False, the program will generate new data.


MAX_GRAPH_DATA_POINTS = 50 # This is the maximum number of data points that can be displayed on the graph at once