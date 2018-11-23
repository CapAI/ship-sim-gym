import time

import gym
import ship_gym
from env.ship_env import ShipEnv

env = ShipEnv(max_steps=1000)

env.reset()
for _ in range(2):
    env.render()

    # ret = env.step(env.action_space.sample()) # take a random action
    ret = env.step(0) # take a random action

    time.sleep(3)
    print(ret)

    # time.sleep(0.0)