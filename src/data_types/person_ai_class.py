import random
import os

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from .constants import *
from .lists import *

from .person_class import Person



class PersonAI(Person):
    def __init__(self, name, age, gender, country):
        super().__init__(name, age, gender, country)
        self.epsilon = 0.9

    def initNetworks(self):
        self.q_networks = []
        # self.price_change_nets = []
        self.state_dim = 8
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')  # Define the device
        # print(torch.cuda.is_available())
        for i in range(len(self.personServices)):
            self.q_networks.append(create_q_network(self.state_dim, 5, i))
            self.q_networks[i].to(device)
            self.q_networks[i].train()
            self.optimizer = optim.Adam(self.q_networks[i].parameters(), lr=0.01)
            self.loss_function = nn.MSELoss()
            self.alpha = 0.9

    def personNext(self):
        for service, i in zip(self.personServices, range(len(self.personServices))):
            state = torch.tensor(self.get_state(service))

            q_price, q_supply = self.q_networks[i](state)
            try:
                self.take_action(service, q_price.item(), q_supply.item())
            except Exception as e:
                return
            reward = self.alpha * self.get_reward(service)
            new_state = torch.tensor(self.get_state(service))

            # Calculate the target Q-value
            target_q_price = (
                reward
                + (1 - self.alpha)
                * self.q_networks[i](new_state)[0]
            )
            target_q_supply = (
                reward
                + (1 - self.alpha)
                * self.q_networks[i](new_state)[1]
            )


            loss_price = self.loss_function(q_price, target_q_price)
            loss_supply = self.loss_function(q_supply, target_q_supply)
            total_loss = loss_price + loss_supply

            self.optimizer.zero_grad()
            total_loss.backward()
            self.optimizer.step()

        
        self.prevBalance = self.balance

    def get_state(self, service):
        state = [
            self.balance,
            self.balance - self.prevBalance,
        ]  # Adding total balance to the state representation
        state.extend(
            [
                service.demand,
                service.supply,
                service.price,
                service.price - service.previousPrice,
                service.revenue,
                service.revenue - service.prevRevenue,
            ]
        )
        return state

                
    def take_action(self, service, price, supply):
        # Define actions for each subject
        supply = int(supply)
        if service.price + price > 0:
            service.price += price
        if service.supply + supply < 0:
            return
        if self.balance > supply * service.costOfNewSupply:
            service.supply += supply
            self.balance -= supply * service.costOfNewSupply


    def get_reward(self, service):
        reward = 0

        if service.revenue < service.prevRevenue:
            reward -= 20  # Penalize with a fixed amount
        else:
            reward += 20

        if self.balance < self.prevBalance:
            reward -= 10 # Penalize with a fixed amount
        else:
            reward += 10

        if service.supply == 0:
            return reward
        if service.demand / service.supply < 0.5 or service.demand / service.supply > 2:
            reward -= 3
        if 0.9 < service.demand / service.supply < 1.1:
            reward += 3

        reward -= service.supply

        return reward

    def save(self):
        for i in range(len(allPeople[0].q_networks)):
            torch.save(allPeople[0].q_networks[i].state_dict(), f"data/networks/q_network{i}.pt")
            #print(f"Model {i} saved successfully")
        #print("All models saved successfully")
        return

# Define the DNN architecture
class QNetwork(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 64)
        #self.fc3 = nn.Linear(64, output_dim)
        self.fc3_price = nn.Linear(64, 1)
        self.fc3_supply = nn.Linear(64, 1)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        #x = self.fc3(x)
        #return x
        change_in_price = self.fc3_price(x)  # Output for changing price
        change_in_supply = self.fc3_supply(x)  # Output for changing supply
        return change_in_price, change_in_supply


def create_q_network(input_dim, output_dim, i):
    model = QNetwork(input_dim, output_dim)
    if os.path.exists("networks/q_network.pt") and read_from_file:
        model.load_state_dict(torch.load(f"networks/q_network{i}.pt"))
        # print(f"Model {i} loaded successfully")
    return model

