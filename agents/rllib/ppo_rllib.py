import random

import ray

from ray.tune import register_env
from ray.tune import run_experiments

if __name__ == "__main__":

    # register_env(env_creator_name, lambda config: ship_gym = gym.make('ShipSim-v0'))

    ray.init()
    run_experiments({
        "demo": {
            "run": "PPO",
            "trial_resources": {"cpu": 1, "gpu": 0},
            "ship_gym": "ShipSim-v0",
            "config": {
                "num_workers" : 0,
                "num_envs_per_worker": 1,
                "timesteps_per_batch": 1000,
                "batch_mode": "truncate_episodes",
            },
        },
    })
