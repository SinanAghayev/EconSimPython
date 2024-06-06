import tensorflow as tf
from tensorflow.keras import layers


class PriceChangeNetwork(tf.keras.Model):
    def __init__(self, state_dim, action_dim):
        super(PriceChangeNetwork, self).__init__()
        self.dense1 = layers.Dense(64, activation="relu")
        self.dense2 = layers.Dense(64, activation="relu")
        self.output_layer = layers.Dense(action_dim)

    def call(self, inputs):
        x = self.dense1(inputs)
        x = self.dense2(x)
        return self.output_layer(x)

    def personNext(self):
        for service, i in zip(self.personServices, range(len(self.personServices))):
            state = self.get_state(service)
            action = self.get_action(state)  # Select action based on the current state
            # Execute action in the environment

            # Update agent's knowledge based on the observed transition
            self.take_action(action, service)  # Perform the selected action
            reward = self.get_reward(
                service, action
            )  # Get reward based on the new state and action

            new_state = self.get_state(service)

            # Calculate the target Q-value
            target_q_value = reward + self.gamma * np.max(
                self.q_networks[i].predict(new_state)
            )

            # Calculate the predicted Q-value
            predicted_q_value = self.q_networks[i].predict(state)[0][action]

            # Calculate the loss
            loss = self.loss_function(target_q_value, predicted_q_value)

            # Update the Q-network
            with tf.GradientTape() as tape:
                gradients = tape.gradient(loss, self.q_networks[i].trainable_variables)
            self.optimizer.apply_gradients(
                zip(gradients, self.q_networks[i].trainable_variables)
            )

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

    def get_reward(self, service, action):
        reward = 0

        # Check the effect of increasing supply on the revenue or demand of the service
        reward = (
            service.revenue * 0.1
        )  # Adjust this calculation as per the desired impact

        if service.revenue < service.prevRevenue:
            reward -= 10  # Penalize with a fixed amount

        if self.balance < self.prevBalance:
            reward -= 10  # Penalize with a fixed amount

        return reward

    def create_price_change_network(self, state_dim, action_dim):
        return PriceChangeNetwork(state_dim, action_dim)

    def get_price_changes(self, state, i):
        # Assume state is flattened and passed as input to the DNN
        return self.price_change_nets[i](state)
