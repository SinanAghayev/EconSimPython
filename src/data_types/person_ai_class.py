import os
import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
from collections import deque

import src.data_types.constants as constants
import src.data_types.config as config
import src.data_types.data_collections as data_collections
from src.data_types.person_class import Person
from src.data_types.service_class import Service


class PersonAI(Person):
    def initVariables(self):
        # PPO hyperparameters
        self.gamma = 0.99  # Discount factor
        self.gae_lambda = 0.95  # GAE lambda
        self.clip_epsilon = 0.2  # PPO clip parameter
        self.entropy_coef = 0.01  # Entropy bonus coefficient
        self.value_coef = 0.5  # Value loss coefficient
        self.max_grad_norm = 0.5  # Gradient clipping
        self.n_epochs = 4  # Number of epochs per update
        self.mini_batch_size = 64  # Mini-batch size for updates
        self.update_frequency = 128  # Steps before policy update

        # Network architecture
        self.state_dim = 8
        self.action_dim = 2  # (price change, supply change)

        # Initialize policy network
        self.policy = ActorCritic(self.state_dim, self.action_dim)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=3e-4)

        # Memory for storing trajectories
        self.memory = PPOMemory()

        # Training statistics
        self.steps_since_update = 0
        self.episode_rewards = []

    def get_state(self, service: Service):
        """Convert service state to normalized feature vector"""
        state = [
            service.demand / (constants.PEOPLE_COUNT + 1e-8),
            service.supply / (constants.PEOPLE_COUNT + 1e-8),
            (service.demand - service.supply) / (constants.PEOPLE_COUNT + 1e-8),
            service.price / (constants.MAX_PRICE + 1e-8),
            (service.price - service.previous_price) / (constants.MAX_PRICE + 1e-8),
            service.revenue / (service.price * constants.PEOPLE_COUNT + 1e-8),
            (service.revenue - service.previous_revenue)
            / (service.price * constants.PEOPLE_COUNT + 1e-8),
            service.bought_recently_count / (constants.PEOPLE_COUNT + 1e-8),
        ]
        return np.array(state, dtype=np.float32)

    def decide_action(self):
        """Sample actions from the policy for all services"""
        self.current_actions = {}
        self.current_log_probs = {}
        self.current_values = {}
        self.current_states = {}

        for service in self.provided_services:
            state = self.get_state(service)
            state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)

            # Get policy predictions
            with torch.no_grad():
                mean, std, value = self.policy(state_tensor)
                dist = torch.distributions.Normal(mean, std)
                action = dist.sample()
                log_prob = dist.log_prob(action).sum(dim=-1)

            # Store for later use
            self.current_states[service.name] = state
            self.current_actions[service.name] = action.squeeze(0)
            self.current_log_probs[service.name] = log_prob.squeeze(0)
            self.current_values[service.name] = value.squeeze(0)

    def apply_action(self):
        """Apply the sampled actions to services"""
        for service in self.provided_services:
            action = self.current_actions[service.name]

            # Convert action from [-1, 1] range to actual changes
            delta_price = action[0].item() * constants.MAX_PRICE_CHANGE
            delta_supply = action[1].item() * constants.MAX_SUPPLY_CHANGE

            # Apply price change with bounds
            new_price = service.price + delta_price
            service.price = np.clip(new_price, constants.MIN_PRICE, constants.MAX_PRICE)

            # Apply supply change with cost consideration
            supply_cost = max(0, delta_supply) * service.cost_of_new_supply

            if delta_supply > 0 and self.balance >= supply_cost:
                # Buying new supply
                service.supply += int(delta_supply)
                self.balance -= supply_cost
            elif delta_supply < 0:
                # Reducing supply (sell back at half cost)
                reduction = int(abs(delta_supply))
                actual_reduction = min(reduction, service.supply)
                service.supply -= actual_reduction
                self.balance += actual_reduction * service.cost_of_new_supply * 0.5

            # Ensure supply is non-negative
            service.supply = max(0, service.supply)

    def store_reward(self):
        """Store transitions in memory after actions are taken"""
        for service in self.provided_services:
            reward = self.get_reward(service)

            self.memory.store(
                state=torch.tensor(
                    self.current_states[service.name], dtype=torch.float32
                ),
                action=self.current_actions[service.name],
                log_prob=self.current_log_probs[service.name],
                value=self.current_values[service.name],
                reward=reward,
                done=False,  # You can set this based on episode termination
            )

        self.steps_since_update += 1

    def should_update(self):
        """Check if we have enough data to perform a policy update"""
        return self.steps_since_update >= self.update_frequency

    def update_policy(self):
        """Perform PPO update on collected trajectories"""
        if len(self.memory.states) == 0:
            return

        # Convert memory to tensors
        states = torch.stack(self.memory.states)
        actions = torch.stack(self.memory.actions)
        old_log_probs = torch.stack(self.memory.log_probs).detach()
        values = torch.stack(self.memory.values).squeeze(-1).detach()
        rewards = torch.tensor(self.memory.rewards, dtype=torch.float32)
        dones = torch.tensor(self.memory.dones, dtype=torch.float32)

        # Compute returns and advantages using GAE
        returns, advantages = self.compute_gae(rewards, values, dones)

        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        # Multiple epochs of optimization
        dataset_size = len(states)

        for epoch in range(self.n_epochs):
            # Shuffle indices for mini-batch sampling
            indices = np.arange(dataset_size)
            np.random.shuffle(indices)

            # Process mini-batches
            for start in range(0, dataset_size, self.mini_batch_size):
                end = min(start + self.mini_batch_size, dataset_size)
                batch_indices = indices[start:end]

                # Get mini-batch data
                batch_states = states[batch_indices]
                batch_actions = actions[batch_indices]
                batch_old_log_probs = old_log_probs[batch_indices]
                batch_advantages = advantages[batch_indices]
                batch_returns = returns[batch_indices]
                batch_values = values[batch_indices]

                # Forward pass
                mean, std, new_values = self.policy(batch_states)
                dist = torch.distributions.Normal(mean, std)
                new_log_probs = dist.log_prob(batch_actions).sum(dim=-1)
                entropy = dist.entropy().mean()

                # Compute PPO actor loss
                ratio = torch.exp(new_log_probs - batch_old_log_probs)
                surr1 = ratio * batch_advantages
                surr2 = (
                    torch.clamp(ratio, 1.0 - self.clip_epsilon, 1.0 + self.clip_epsilon)
                    * batch_advantages
                )
                actor_loss = -torch.min(surr1, surr2).mean()

                # Compute clipped value loss
                new_values_squeezed = new_values.squeeze(-1)
                value_pred_clipped = batch_values + torch.clamp(
                    new_values_squeezed - batch_values,
                    -self.clip_epsilon,
                    self.clip_epsilon,
                )
                value_loss_unclipped = (batch_returns - new_values_squeezed).pow(2)
                value_loss_clipped = (batch_returns - value_pred_clipped).pow(2)
                critic_loss = (
                    0.5 * torch.max(value_loss_unclipped, value_loss_clipped).mean()
                )

                # Total loss
                loss = (
                    actor_loss
                    + self.value_coef * critic_loss
                    - self.entropy_coef * entropy
                )

                # Optimization step
                self.optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(
                    self.policy.parameters(), self.max_grad_norm
                )
                self.optimizer.step()

        # Clear memory after update
        self.memory.clear()
        self.steps_since_update = 0

    def compute_gae(self, rewards, values, dones):
        """Compute Generalized Advantage Estimation"""
        advantages = []
        gae = 0

        # Add a zero value for the terminal state
        next_values = torch.cat([values[1:], torch.tensor([0.0])])

        for t in reversed(range(len(rewards))):
            # TD error
            delta = (
                rewards[t] + self.gamma * next_values[t] * (1 - dones[t]) - values[t]
            )

            # GAE
            gae = delta + self.gamma * self.gae_lambda * (1 - dones[t]) * gae
            advantages.insert(0, gae)

        advantages = torch.tensor(advantages, dtype=torch.float32)
        returns = advantages + values

        return returns, advantages

    def get_reward(self, service: Service):
        """Compute reward for a service based on performance"""
        reward = 0.0

        # Reward for units sold
        reward += service.bought_recently_count

        # Revenue-based reward
        if service.revenue > service.previous_revenue:
            reward += 4.0
        elif service.revenue < service.previous_revenue:
            reward -= 1.0

        # Penalize zero revenue
        if service.revenue <= 0:
            reward -= 10.0

        # Penalize pricing below cost
        if service.price < service.cost_of_new_supply:
            reward -= 3.0

        # Reward for meeting demand (supply-demand balance)
        if max(service.demand, service.supply) > 0:
            # Penalize excess supply
            if service.supply > service.demand:
                excess_ratio = (service.supply - service.demand) / (
                    service.supply + 1e-8
                )
                reward -= excess_ratio * 1.0

        # Reward for maintaining stock
        if service.supply > 0:
            reward += 3.0

        return reward

    def save(self):
        """Save the policy network"""
        save_dir = "data/networks"
        os.makedirs(save_dir, exist_ok=True)

        checkpoint = {
            "policy_state_dict": self.policy.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "episode_rewards": self.episode_rewards,
        }

        torch.save(checkpoint, f"{save_dir}/ppo_agent.pt")
        print(f"Model saved to {save_dir}/ppo_agent.pt")

    def load(self):
        """Load the policy network"""
        checkpoint_path = "data/networks/ppo_agent.pt"

        if os.path.exists(checkpoint_path):
            checkpoint = torch.load(checkpoint_path)
            self.policy.load_state_dict(checkpoint["policy_state_dict"])
            self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
            self.episode_rewards = checkpoint.get("episode_rewards", [])
            print(f"Model loaded from {checkpoint_path}")
        else:
            print(f"No checkpoint found at {checkpoint_path}, starting fresh")


class ActorCritic(nn.Module):
    """Actor-Critic network for PPO"""

    def __init__(self, input_dim, output_dim):
        super().__init__()

        # Shared feature extraction
        self.shared = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
        )

        # Actor network (policy)
        self.actor_mean = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim),
            nn.Tanh(),  # Output in [-1, 1]
        )

        # Learnable log standard deviation
        self.log_std = nn.Parameter(torch.zeros(output_dim))

        # Critic network (value function)
        self.critic = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )

    def forward(self, obs):
        """Forward pass through both actor and critic"""
        shared_features = self.shared(obs)

        # Actor outputs
        mean = self.actor_mean(shared_features)
        std = torch.exp(self.log_std).clamp(min=1e-6, max=2.0)

        # Critic output
        value = self.critic(shared_features)

        return mean, std, value


class PPOMemory:
    """Memory buffer for storing trajectories"""

    def __init__(self):
        self.states = []
        self.actions = []
        self.log_probs = []
        self.values = []
        self.rewards = []
        self.dones = []

    def store(self, state, action, log_prob, value, reward, done=False):
        """Store a single transition"""
        self.states.append(state)
        self.actions.append(action)
        self.log_probs.append(log_prob)
        self.values.append(value)
        self.rewards.append(reward)
        self.dones.append(done)

    def clear(self):
        """Clear all stored transitions"""
        self.__init__()

    def __len__(self):
        return len(self.states)
