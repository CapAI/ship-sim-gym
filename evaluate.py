import json
import os
import random

import ray
from ray.rllib.agents.agent import get_agent_class
from ray.rllib.agents.ppo import ppo

from ray import tune
from ray.tune import run_experiments, tune, register_env
from ray.tune.logger import pretty_print
from ray.tune.schedulers import PopulationBasedTraining

from ship_gym.config import GameConfig, EnvConfig
from ship_gym.game import ShipGame
from ship_gym.ship_env import ShipEnv

game_config = GameConfig
game_config.FPS = 30
game_config.SPEED = 1
game_config.DEBUG = True
game_config.BOUNDS = (500, 500)

def env_creator(env_config):

	env_config = EnvConfig
	env = ShipEnv(game_config, env_config)

	return env

def rollout(config_dir):


    # Load configuration from file

    config_path = os.path.join(config_dir, "params.json")
    if not os.path.exists(config_path):
        config_path = os.path.join(config_dir, "../params.json")
    if not os.path.exists(config_path):
        raise ValueError(
            "Could not find params.json in either the checkpoint dir or "
            "its parent directory.")
    with open(config_path) as f:
        config = json.load(f)
    if "num_workers" in config:
        config["num_workers"] = min(2, config["num_workers"])


    ray.init()

    cls = get_agent_class("PPO")

    agent = cls(env=env_creator, config=config)



    agent.restore(args.checkpoint)
    num_steps = 1000

    rollouts = []
    steps = 0
    while steps < (num_steps or steps + 1):
        # if args.out is not None:
        rollout = []
        state = env.reset()
        done = False
        reward_total = 0.0
        while not done and steps < (num_steps or steps + 1):
            action = agent.compute_action(state)
            next_state, reward, done, _ = env.step(action)
            reward_total += reward
            # if not args.no_render:
            #     env.render()
            # if args.out is not None:
            rollout.append([state, action, next_state, reward, done])
            steps += 1
            state = next_state

            rollouts.append(rollout)
        print("Episode reward", reward_total)
    # if args.out is not None:
    #     pickle.dump(rollouts, open(args.out, "wb"))


if __name__ == "__main__":


    # Can optionally call agent.restore(path) to load a checkpoint.
	path = "/home/simons/ray_results/pbt_ship_sim_v2/PPO_ShipGym-v1_1_num_sgd_iter=30,sgd_minibatch_size=2048,train_batch_size=40000_2018-12-05_17-41-41woi3j510/"
	rollout(path)

