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
