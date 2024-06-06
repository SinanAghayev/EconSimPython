import random
import os

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from constants import *
from lists import *
from priceChangeNN import PriceChangeNetwork
from personClass import Person
import torch


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
            self.gamma = 0.9

    def personNext(self):
        for service, i in zip(self.personServices, range(len(self.personServices))):
            state = torch.tensor(self.get_state(service))
            """
            action, dummy = self.get_action(
                state, i
            )  # Select action based on the current state
            # Execute action in the environment

            #if dummy < 0:
             #   continue

            # Update agent's knowledge based on the observed transition
            self.take_action(action, service)  # Perform the selected action
            reward = self.get_reward(
                service, action
            )  # Get reward based on the new state and action
            """
            q_price, q_supply = self.q_networks[i](state)
            try:
                self.take_action_new(service, q_price.item(), q_supply.item())
            except Exception as e:
                return
            reward = self.gamma * self.get_reward_new(service)
            new_state = torch.tensor(self.get_state(service))

            # Calculate the target Q-value
            target_q_price = (
                reward
                + (1 - self.gamma)
                * self.q_networks[i](new_state)[0]
            )
            target_q_supply = (
                reward
                + (1 - self.gamma)
                * self.q_networks[i](new_state)[1]
            )

            # Use the Q-network to predict Q-values for the given state
            
            # Choose the action with the highest Q-value
            ##action_index = torch.argmax(q_values)
            # Get the predicted Q-value for the chosen action
            ##predicted_q_value = q_values[action_index]

            loss_price = self.loss_function(q_price, target_q_price)
            loss_supply = self.loss_function(q_supply, target_q_supply)
            total_loss = loss_price + loss_supply

            self.optimizer.zero_grad()
            total_loss.backward()
            self.optimizer.step()

            # print(action, self.balance)

            #print(f"Target Q value shape: {target_q_value}")
            #print(f"Predicted Q value shape: {predicted_q_value}")
            #print(f"Target Q value shape: {target_q_value}")
            #print(f"Predicted Q value shape: {predicted_q_value}")
            # Calculate the loss

            #self.optimizer.zero_grad()
            #loss = self.loss_function(target_q_value, predicted_q_value)
            #loss.backward()
            #self.optimizer.step()
        
        self.prevBalance = self.balance

    def get_action(self, state, i):
        # Use the Q-network to predict Q-values for the given state
        q_values = self.q_networks[i](state)

        # Choose the action with the highest Q-value
        action_index = torch.argmax(q_values).item()
        actions = [
            "increase_price",
            "decrease_price", 
            "add_supply",
            "remove_supply",
            "do_nothing",
        ]  # List of possible actions
        action = actions[action_index]  # Get the action corresponding to the index

        return action_index, torch.max(q_values).item()

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

    def take_action(self, action, service):
        if random.random() > self.epsilon:
            action = random.randint(0, 4)
        # Define actions for each subject
        if action == 0:
            service.price += service.price * random.uniform(0, 0.1)
        if action == 1:
            service.price -= service.price * random.uniform(0, 0.1)
        elif action == 2:
            if self.balance > 10 * service.costOfNewSupply:
                service.supply += 10
                self.balance -= 10 * service.costOfNewSupply
        elif action == 3:
            if service.supply > 10:
                service.supply -= 10
                self.balance += 10 * service.costOfNewSupply
                
    def take_action_new(self, service, price, supply):
        # Define actions for each subject
        supply = int(supply)
        if service.price + price > 0:
            service.price += price
        if service.supply + supply < 0:
            return
        if self.balance > supply * service.costOfNewSupply:
            service.supply += supply
            self.balance -= supply * service.costOfNewSupply

    def get_reward(self, service, action):
        reward = 0

        # Check the effect of increasing supply on the revenue or demand of the service
        #reward = (
        #    (service.revenue - service.prevRevenue) * 0.1
        #)  # Adjust this calculation as per the desired impact

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

        return reward

    def get_reward_new(self, service):
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

    def create_price_change_network(self, state_dim, action_dim):
        return PriceChangeNetwork(state_dim, action_dim)

    def get_price_changes(self, state, i):
        # Assume state is flattened and passed as input to the DNN
        return self.price_change_nets[i](state)

    def save(self):
        for i in range(len(allPeople[0].q_networks)):
            torch.save(allPeople[0].q_networks[i].state_dict(), f"networks/q_network{i}.pt")
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

