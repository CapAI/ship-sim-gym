import ray

from ray.tune import register_env
from ray.tune import run_experiments    

from ship_env import ShipEnv

env_creator_name = "ShipSim-v0"
register_env(env_creator_name, lambda config: ShipEnv())
ray.init()
run_experiments({
    "demo": {
        "run": "PPO",
        "trial_resources": {"cpu": 1},
        "ship_gym": "ShipSim-v0",
        "config": {
            "num_workers" : 0,
            "num_envs_per_worker": 1
        },

    },
})