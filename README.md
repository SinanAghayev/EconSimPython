# RL-Based Economic Simulation

This project is an agent-based economic simulation that models supply–demand dynamics, pricing strategies, and capital constraints in a simplified market environment. The project explores how reinforcement learning agents (PPO) adapt pricing and supply decisions over time based on market feedback.

## Project Motivation

The goal of this project is to simulate bounded rational economic agents and observe how pricing, production, and balance evolve under realistic constraints such as limited capital, changing demand, and over- or under-supply penalties.

Rather than using fixed heuristics, agents learn their strategies through interaction with the environment.

## Key Features

- **Agent-Based Economic Simulation:** Individuals provide services with dynamic pricing and supply. Demand emerges from population behavior, and capital and production costs constrain decisions.

- **Reinforcement Learning (PPO):** Actor–Critic architecture using Proximal Policy Optimization with a continuous action space for price and supply adjustments. Reward shaping is based on revenue, demand fulfillment, and sustainability.

- **Adaptive AI Agents:** Agents learn pricing and production strategies over time, balancing exploration and exploitation via entropy regularization. A shared policy is used across multiple services per agent.

- **Real-Time Visualization:** Live graphs display the evolution of price, demand, supply, and balance during the simulation. Visualization can be toggled at runtime.

- **Interactive Simulation Control:** Core economic parameters can be modified via configuration files, and keyboard controls allow switching between visualization modes.

## Technical Stack

Python  
PyTorch (PPO, Actor–Critic)  
NumPy  
Matplotlib  
Custom entity-based simulation framework  

## Getting Started
### Prerequisites

Python 3.x  
Required packages listed in requirements.txt  

### Installation

Clone the repository:

`git clone https://github.com/yourusername/EconSimPython.git`

Navigate to the project directory:

`cd EconSimPython`

Install dependencies:

`pip install -r requirements.txt`

### Running the Simulation

Run the main simulation loop:

`python main.py`

The simulation progresses in discrete time steps (“days”), updating service prices, supply levels, demand, and agent balances.

Core economic parameters can be adjusted in:

`src/data_types/constants.py`

### Controls

V — Run simulation with visualization enabled  
B — Run simulation without graphics

## Learning Outcomes

### This project explores and demonstrates:

Proximal Policy Optimization with Generalized Advantage Estimation
Continuous control in economic environments
Reward shaping for multi-objective optimization
Designing simulations around interacting economic entities

## Future Improvements

Multi-agent competition and market dynamics
Episode termination logic and curriculum learning
More realistic consumer behavior models
External market shocks and policy interventions

## Contributing

Contributions, feedback, and discussions are welcome.
