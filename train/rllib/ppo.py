import random

import ray
from ray.rllib.agents.ppo import ppo
from ray.tune import run_experiments, tune, register_env

from ray import tune
from ray.tune.schedulers import PopulationBasedTraining

from ship_gym.game import ShipGame
from ship_gym.ship_env import ShipEnv

if __name__ == "__main__":

    # register_env(env_creator_name, lambda config: ship_gym = gym.make('ShipSim-v0'))

    ray.init(num_gpus=1)

    def env_creator(env_config):

        game = ShipGame(speed=20, fps=10000, bounds=(800, 800))
        env = ShipEnv(game, env_config)

        print(env_config)

        return env

    experiments = {
        "find-lr": {
            "run": "PPO",
            "stop": {
                "time_total_s":180
            },
            "env": "ship-gym-v1",
            "config": {
                "num_gpus": 1,
                "num_workers" : 10,
                "lr" : tune.grid_search([0.001, 0.0001, 0.00001]),
                "env_config": {
                    "n_goals": 5
                }
            },
        },
    }
    tune.register_env("ship-gym-v1", env_creator)
    tune.run_experiments(experiments)
