import random

import ray
from ray.rllib.agents.ppo import ppo

from ray import tune

from ship_gym.game import ShipGame
from ship_gym.ship_env import ShipEnv

if __name__ == "__main__":

    # register_env(env_creator_name, lambda config: ship_gym = gym.make('ShipSim-v0'))

    ray.init()

    def env_creator(env_config):

        game = ShipGame(speed=20, fps=10000, bounds=(800, 800))
        env = ShipEnv(game, env_config)

        print(env_config)

        return env

    tune.register_env("ship-gym-v1", env_creator)
    tune.run_experiments({
        "demo": {
            "run": "PPO",
            # "trial_resources": {"cpu": 12, "gpu": 1},
            "env": "ship-gym-v1",
            "config": {
                "num_gpus": 1,
                "num_workers" : 10,
                "lr" : tune.grid_search([0.001, 0.0001, 0.00001]),
                # "lr_schedule" : "linear",
                "env_config": {
                    "n_goals": 5
                }
            },
        },
    })
