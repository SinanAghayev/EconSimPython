import os
import torch
import torch.nn as nn
import torch.optim as optim
import random

from data_types.person_class import Person
from data_types.constants import *

class PersonAI(Person):
    def __init__(self, name, age, gender, country):
        super().__init__(name, age, gender, country)
        self.epsilon = 0.9

    def initNetworks(self):
        self.q_price_networks = []
        self.q_supply_networks = []
        self.price_optimizer = []
        self.supply_optimizer = []
        self.state_dim = 9
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        for i in range(len(self.personServices)):
            self.q_price_networks.append(create_q_network(self.state_dim, 1, i, "price"))
            self.q_price_networks[i].to(device)
            self.q_price_networks[i].train()

            self.q_supply_networks.append(create_q_network(self.state_dim, 1, i, "supply"))
            self.q_supply_networks[i].to(device)
            self.q_supply_networks[i].train()

            self.price_optimizer.append(optim.Adam(self.q_price_networks[i].parameters(), lr=0.01))
            self.supply_optimizer.append(optim.Adam(self.q_supply_networks[i].parameters(), lr=0.01))

        self.loss_function = nn.MSELoss()
        self.alpha = 0.9
        self.q_price = [None] * len(self.personServices)
        self.q_supply = [None] * len(self.personServices)

    def personNext(self):
        for service, i in zip(self.personServices, range(len(self.personServices))):
            state = torch.tensor(self.get_state(service), dtype=torch.float32)

            # Epsilon-greedy action selection for price
            if random.random() < self.epsilon:
                self.q_price[i] = self.q_price_networks[i](state)
            else:
                self.q_price[i] = torch.tensor([random.uniform(-1, 1)], dtype=torch.float32, requires_grad=True)

            # Epsilon-greedy action selection for supply
            if random.random() < self.epsilon:
                self.q_supply[i] = self.q_supply_networks[i](state)
            else:
                self.q_supply[i] = torch.tensor([random.uniform(-1, 1)], dtype=torch.float32, requires_grad=True)

            self.take_action(service, self.q_price[i].item(), self.q_supply[i].item())

        self.prevBalance = self.balance

    def backpropagate(self):
        for service, i in zip(self.personServices, range(len(self.personServices))):

            # Direct Q-value update using observed reward
            target_q_price = self.get_price_reward(service)
            target_q_supply = self.get_supply_reward(service)

            loss_price = self.loss_function(self.q_price[i], torch.tensor([target_q_price], dtype=torch.float32))
            loss_supply = self.loss_function(self.q_supply[i], torch.tensor([target_q_supply], dtype=torch.float32))

            self.price_optimizer[i].zero_grad()
            loss_price.backward()
            self.price_optimizer[i].step()

            self.supply_optimizer[i].zero_grad()
            loss_supply.backward()
            self.supply_optimizer[i].step()

    def get_state(self, service):
        state = [
            self.balance,
            self.balance - self.prevBalance,
        ]
        state.extend(
            [
                service.demand,
                service.supply,
                service.demand - service.supply,
                service.price,
                service.price - service.previousPrice,
                service.revenue,
                service.revenue - service.prevRevenue,
            ]
        )
        return state

    def take_action(self, service, price, supply):
        supply = int(supply)
        if service.price + price > 0:
            service.price += price
        if service.supply + supply < 0:
            return
        if self.balance > supply * service.costOfNewSupply:
            service.supply += supply
            self.balance -= supply * service.costOfNewSupply

    def get_price_reward(self, service):
        reward = 0

        if service.bought_recently_count == 0:
            reward -= 75
        else:
            reward += service.bought_recently_count

        if service.revenue < service.prevRevenue:
            reward -= 20
        else:
            reward += 20

        if self.balance < self.prevBalance:
            reward -= 5
        else:
            reward += 5

        return reward
    
    def get_supply_reward(self, service):
        reward = 0

        if service.revenue < service.prevRevenue:
            reward -= 10
        else:
            reward += 10

        if self.balance < self.prevBalance:
            reward -= 5
        else:
            reward += 5

        if service.supply < 2:
            return reward
        if service.demand / service.supply < 0.5 or service.demand / service.supply > 2:
            reward -= 5
        if 0.9 < service.demand / service.supply < 1.1:
            reward += 20

        reward += service.demand - service.supply

        return reward

    def save(self):
        for i in range(len(self.q_price_networks)):
            torch.save(self.q_price_networks[i].state_dict(), f"data/networks/q_price_network{i}.pt")
            torch.save(self.q_supply_networks[i].state_dict(), f"data/networks/q_supply_network{i}.pt")
        return

# Define the DNN architecture
class QNetwork(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, output_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

def create_q_network(input_dim, output_dim, i, network_type):
    model = QNetwork(input_dim, output_dim)
    if os.path.exists(f"data/networks/q_{network_type}_network{i}.pt") and read_networks_from_file:
        model.load_state_dict(torch.load(f"data/networks/q_{network_type}_network{i}.pt"))
    return model
