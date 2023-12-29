import random
from constants import *
from lists import *
from priceChangeNN import PriceChangeNetwork
import tensorflow as tf
from tensorflow.keras import layers
from personClass import Person


class PersonAI(Person):
    def __init__(self, name, age, gender, country):
        super().__init__(name, age, gender, country)

    def initNetworks(self):
        self.q_network = create_q_network(len(self.personServices) * 6 + 2, 3)
        # Initialize PriceChangeNetwork
        self.price_change_net = self.create_price_change_network(
            len(self.personServices) * 6 + 2, 1
        )

    def personNext(self):
        for service in self.personServices:
            state = self.get_state()

            action = self.get_action(state)  # Select action based on the current state
            # Execute action in the environment

            # Update agent's knowledge based on the observed transition
            self.take_action(action, service)  # Perform the selected action
            self.get_reward(
                service, action
            )  # Get reward based on the new state and action

    def get_action(self, state):
        # Use the Q-network to predict Q-values for the given state
        q_values = self.q_network(
            tf.convert_to_tensor(state)
        )  # Assuming state is a list or array

        # Choose the action with the highest Q-value
        action_index = tf.argmax(
            q_values[0]
        ).numpy()  # Extract the index of the action with the highest Q-value
        actions = [
            "adjust_price",
            "add_supply",
            "remove_supply",
        ]  # List of possible actions
        action = actions[action_index]  # Get the action corresponding to the index

        return action

    def get_state(self):
        state = [
            self.balance,
            self.balance - self.prevBalance,
        ]  # Adding total balance to the state representation
        for service in self.personServices:
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
        # Define actions for each subject
        if action == "adjust_price":
            service.price += self.get_price_changes()
        elif action == "add_supply":
            if self.balance > 20 * service.price():
                service.supply += 20
                self.balance -= 20 * service.price()
        elif action == "remove_supply":
            if service.supply > 20:
                service.supply -= 20
                self.balance += 20 * service.price()

    def get_reward(self, service, action):
        # Calculate reward based on the effect of the action taken by the agent

        # For instance, consider a simple scenario where increasing supply yields positive reward
        if action == "add_supply":
            # Check the effect of increasing supply on the revenue or demand of the service
            reward = (
                service.revenue * 0.1
            )  # Adjust this calculation as per the desired impact

        # Alternatively, penalize the agent for actions that result in a negative effect
        elif action == "adjust_price":
            # Penalize if the price adjustment leads to decreased revenue or demand
            if service.revenue < service.prevRevenue:
                reward = -10  # Penalize with a fixed amount

        # If the action doesn't have a significant effect or other criteria, assign a neutral reward
        else:
            reward = 0

        return reward

    def create_price_change_network(self, state_dim, action_dim):
        return PriceChangeNetwork(state_dim, action_dim)

    def get_price_changes(self, state):
        # Assume state is flattened and passed as input to the DNN
        return self.price_change_net(state)


# Define the DNN architecture
def create_q_network(input_dim, output_dim):
    model = tf.keras.Sequential(
        [
            layers.Dense(64, activation="relu", input_shape=(input_dim,)),
            layers.Dense(64, activation="relu"),
            layers.Dense(output_dim),  # Output layer, output_dim neurons for Q-values
        ]
    )
    return model
