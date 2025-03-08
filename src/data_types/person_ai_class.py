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

    def initVariables(self):
        self.memory = [[] for _ in self.personServices]
        self.current_action = [None] * len(self.personServices)
        self.current_log_prob = [None] * len(self.personServices)
        self.current_value = [None] * len(self.personServices)
        self.current_state = [None] * len(self.personServices)
        self.initNetworks()

    def initNetworks(self):
        self.q_networks = {}
        self.optimizers = {}
        self.state_dim = 8
        self.action_dim = 2  # (price change, supply change)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        for service in self.personServices:
            self.q_networks[service.name] = create_q_network(
                self.state_dim, self.action_dim, service.name
            )
            self.q_networks[service.name].to(device)
            self.q_networks[service.name].train()

            self.optimizers[service.name] = optim.Adam(
                self.q_networks[service.name].parameters(), lr=0.01
            )

        self.loss_function = nn.MSELoss()

    def decide_action(self):
        for i, service in enumerate(self.personServices):
            state = self.get_state(service)
            self.current_state[i] = torch.tensor(state, dtype=torch.float32).unsqueeze(
                0
            )

            # Price action
            mean, std, value = self.q_networks[service.name](self.current_state[i])
            dist = torch.distributions.Normal(mean, std)
            action = dist.sample()
            log_prob = dist.log_prob(action).sum(-1)

            self.current_action[i] = action
            self.current_log_prob[i] = log_prob
            self.current_value[i] = value

    def apply_action(self):
        for i, service in enumerate(self.personServices):
            self.take_action(
                service,
                self.current_action[i][0][0].item(),
                self.current_action[i][0][1].item(),
            )

    def store_reward(self):
        for i, service in enumerate(self.personServices):
            reward = self.get_reward(service)

            self.memory[i].append(
                (
                    self.current_state[i],
                    self.current_action[i],
                    self.current_log_prob[i],
                    self.current_value[i],
                    reward,
                )
            )

    def backpropagate(self):
        gamma = 0.99
        clip_epsilon = 0.2

        for i, service in enumerate(self.personServices):
            for _ in range(4):
                s_name = service.name
                self._ppo_update(
                    self.q_networks[s_name],
                    self.optimizers[s_name],
                    self.memory[i],
                    gamma,
                    clip_epsilon,
                )
            self.memory[i] = []

    def _ppo_update(self, network, optimizer, memory, gamma, clip_epsilon):
        states, actions, log_probs, values, rewards = zip(*memory)
        states = torch.cat(states)
        actions = torch.cat(actions)
        log_probs = torch.cat(log_probs).detach()
        values = torch.cat(values).squeeze(-1).detach()
        rewards = torch.tensor(rewards, dtype=torch.float32)

        returns = []
        future_return = 0

        for step in reversed(range(len(rewards))):
            future_return = rewards[step] + gamma * future_return
            returns.insert(0, future_return)

        returns = torch.tensor(returns, dtype=torch.float32)

        advantages = returns - values.detach()

        # Re-evaluate actions with current policy
        mean, std, current_values = network(states)
        # print(f"{states=}")
        dist = torch.distributions.Normal(mean, std)
        new_log_probs = dist.log_prob(actions).sum(-1)

        # PPO loss
        ratio = torch.exp(new_log_probs - log_probs)
        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1 - clip_epsilon, 1 + clip_epsilon) * advantages
        actor_loss = -torch.min(surr1, surr2).mean()
        critic_loss = ((returns - current_values.squeeze(-1)) ** 2).mean()

        loss = actor_loss + 0.5 * critic_loss - 0.01 * dist.entropy().mean()

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    def get_state(self, service):
        """
        state = [
            self.balance,
            self.balance - self.prevBalance,
        ]
        """
        state = [
            service.demand / (PEOPLE_COUNT),
            service.supply / (PEOPLE_COUNT),
            (service.demand - service.supply) / (PEOPLE_COUNT),
            service.price / MAX_PRICE,
            (service.price - service.previousPrice) / MAX_PRICE,
            service.revenue / (service.price * PEOPLE_COUNT),
            (service.revenue - service.prevRevenue) / (service.price * PEOPLE_COUNT),
            service.bought_recently_count / PEOPLE_COUNT,
        ]
        return state

    def take_action(self, service, price_change, supply_change):
        supply_change = int(supply_change)

        service.price = max(service.price + price_change, 1)

        if service.supply + supply_change < 0:
            self.balance += service.supply * service.price / 2
            service.supply = 0
        elif self.balance > abs(supply_change) * service.costOfNewSupply:
            service.supply += supply_change
            self.balance -= supply_change * service.costOfNewSupply

    def get_reward(self, service):
        reward = 0

        reward += service.bought_recently_count

        if service.revenue <= 0:
            reward -= 10
        elif service.revenue < service.prevRevenue:
            reward -= 1
        else:
            reward += 10

        if service.price < service.costOfNewSupply:
            reward -= 2

        if max(service.demand, service.supply) == 0:
            return reward

        reward += (
            (service.demand - service.supply) / max(service.demand, service.supply) * 2
        )
        return reward

    def save(self):
        for service in self.personServices:
            torch.save(
                self.q_networks[service.name].state_dict(),
                f"data/networks/q_network_{service.name}.pt",
            )


# Define the DNN architecture
class QNetwork(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.actor = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim * 2),  # Mean and LogStd for each action
        )
        self.critic = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )

    def forward(self, obs):
        x = self.actor(obs)
        mean, log_std = torch.chunk(x, 2, dim=-1)
        std = torch.exp(log_std).clamp(min=1e-6, max=1000)

        if torch.any(torch.isnan(mean)) or torch.any(torch.isinf(mean)):
            print("M")
            print(f"Warning: NaN or Inf detected in mean: {mean}")
            mean = torch.zeros_like(
                mean
            )  # Replace NaN or Inf with zeros (or another appropriate value)

        if torch.any(torch.isnan(std)) or torch.any(torch.isinf(std)):
            print("STD")
            print(f"Warning: NaN or Inf detected in std: {std}")
            std = torch.ones_like(
                std
            )  # Replace NaN or Inf with ones (or another appropriate value)

        value = self.critic(obs)
        return mean, std, value


def create_q_network(input_dim, action_dim, service_name):
    model = QNetwork(input_dim, action_dim)
    if (
        os.path.exists(f"data/networks/q_network_{service_name}.pt")
        and read_networks_from_file
    ):
        model.load_state_dict(torch.load(f"data/networks/q_network_{service_name}.pt"))
    return model
