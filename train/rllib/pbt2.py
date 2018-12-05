# Postprocess the perturbed config to ensure it's still valid
import random

import ray
from ray.tune import run_experiments, tune, register_env

from ray.tune.schedulers import PopulationBasedTraining

from ship_gym.config import GameConfig, EnvConfig
from ship_gym.ship_env import ShipEnv

import multiprocessing

if __name__ == '__main__':

    game_config = GameConfig
    game_config.FPS = 1000
    game_config.SPEED = 30
    game_config.BOUNDS = (1000, 1000)



    def env_creator(env_config):

        env_config = EnvConfig
        env = ShipEnv(game_config, env_config)

        return env

    register_env("ShipGym-v1", env_creator)

    def explore(config):
        # ensure we collect enough timesteps to do sgd
        if config["train_batch_size"] < config["sgd_minibatch_size"] * 2:
            config["train_batch_size"] = config["sgd_minibatch_size"] * 2
        # ensure we run at least one sgd iter
        if config["num_sgd_iter"] < 1:
            config["num_sgd_iter"] = 1
        return config


    pbt = PopulationBasedTraining(
        time_attr="time_total_s",
        reward_attr="episode_reward_mean",
        perturbation_interval=600, # 10 mins
        resample_probability=0.33,

        # Specifies the mutations of these hyperparams
        hyperparam_mutations={
            "lambda": lambda: random.uniform(0.9, 1.0),
            "clip_param": lambda: random.uniform(0.01, 0.5),
            "lr": [1e-3, 5e-4, 1e-4, 5e-5, 1e-5],
            "num_sgd_iter": lambda: random.randint(1, 30),
            "sgd_minibatch_size": lambda: random.randint(128, 16384),
            "train_batch_size": lambda: random.randint(2000, 160000),
        })

    ray.init()

    n_goals = 5
    reward_done = .9*n_goals
    
    run_experiments(
        {
            "pbt_ship_sim_v2": {
                "run": "PPO",
                "env": "ShipGym-v1",
                "num_samples": 12, # Repeat the experiment this many times
                # "stop": {
                #     'episode_reward_mean': reward_done
                # },
                "checkpoint_at_end" : True,
                "checkpoint_freq" : 10,
                "config": {
                    # "env_config": {
                    #     "n_goals": n_goals
                    # },
                    "kl_coeff": 1.0,
                    "num_workers": multiprocessing.cpu_count() - 1,
                    "num_gpus": 1,

                    # This gives me the strangest errors!
                    # "model": {
                    #     "free_log_std": True
                    # },
                    # These params are tuned from a fixed starting value.
                    "lambda": 0.95,
                    "clip_param": 0.2,
                    "lr" : 5.0e-4,

                    # These params start off randomly drawn from a set.
                    # "lr":
                    	# lambda spec: random.choice([1e-3, 5e-4, 1e-4, 5e-5, 1e-5]),
                    "num_sgd_iter":
                        lambda spec: random.choice([10, 20, 30]),
                    "sgd_minibatch_size":
                        lambda spec: random.choice([128, 512, 2048]),
                    "train_batch_size":
                        lambda spec: random.choice([10000, 20000, 40000])
                },
            },
        },
        scheduler=pbt)