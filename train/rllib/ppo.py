import random

import ray
from ray.rllib.agents.ppo import ppo
from ray.tune import run_experiments, tune, register_env

from ray import tune
from ray.tune.schedulers import PopulationBasedTraining

from ship_gym.game import ShipGame

from ship_gym.config import GameConfig, EnvConfig
from ship_gym.ship_env import ShipEnv

import multiprocessing

if __name__ == "__main__":

    # register_env(env_creator_name, lambda config: ship_gym = gym.make('ShipSim-v0'))

    game_config = GameConfig
    game_config.FPS = 100000
    game_config.SPEED = 40
    game_config.BOUNDS = (1000, 1000)

    ray.init(num_gpus=1)

    def env_creator(env_config):

        env_config = EnvConfig
        env = ShipEnv(game_config, env_config)

        return env

    experiments = {
        "shipgym_best": {
            "run": "PPO",
            "stop": {
                "time_total_s": 12 * 60 * 60 # 12 hours
            },
            "env": "ship-gym-v1",
            "config": {
            	"num_gpus": 1,
                "num_workers" : multiprocessing.cpu_count() - 1,
                "num_sgd_iter" :  10,
                "sgd_minibatch_size" : 2048,
                "train_batch_size" : 10000,
                "lr_schedule" : [[0, 0.001], [5e6, 0.0001], [1e7, 0.00001]]
            },
        },
    }
    tune.register_env("ship-gym-v1", env_creator)
    tune.run_experiments(experiments)
