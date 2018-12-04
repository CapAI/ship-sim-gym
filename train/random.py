import time

import gym
import ship_gym
from ship_gym.ship_env import ShipEnv

from ship_gym.config import EnvConfig, GameConfig

env = ShipEnv(game_config=GameConfig, env_config=EnvConfig)

env.reset()

for _ in range(10):

    total_reward = 0
    for _ in range(100):
        env.render()

        # ret = ship_gym.step(ship_gym.action_space.sample()) # take a random action
        ret = env.step(0) # take a random action
        total_reward += ret[1]

        if ret[2] == True:
            print("AGENT IS DONE!")
            print(f"TOTAL REWARD = {total_reward}")
            env.reset()
            break

        time.sleep(0.2)
        print(ret)

        # time.sleep(0.0)