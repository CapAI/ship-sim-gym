import ray
from ray import tune
from ray.tune.schedulers import PopulationBasedTraining

from ship_gym.game import ShipGame
from ship_gym.ship_env import ShipEnv

if __name__ == "__main__":
    ray.init(num_gpus=1)

    def env_creator(env_config):
        game = ShipGame(speed=20, fps=10000, bounds=(800, 800))
        env = ShipEnv(game, env_config)

        return env

    tune.register_env("ship-gym-v1", env_creator)

    experiments = {
        "demo": {
            "run": "PPO",
            # "trial_resources": {"cpu": 12, "gpu": 1},
            "env": "ship-gym-v1",
            "config": {
                "num_workers": 10,
                "env_config": {
                    "n_goals": 5
                },
            },
            "stop": {
                'episode_reward_mean': 4.0
            }
        },
    }

    pbt_scheduler = PopulationBasedTraining(
        reward_attr='episode_reward_mean',
        time_attr='time_total_s',
        perturbation_interval=600.0,
        hyperparam_mutations={
            "lr": [1e-3, 5e-4, 1e-4, 5e-5, 1e-5],
            'sgd_batchsize': [128, 256, 512]
        })

    tune.run_experiments(experiments, scheduler=pbt_scheduler)