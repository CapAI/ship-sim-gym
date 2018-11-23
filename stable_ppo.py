import time

import numpy as np
from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2

from env.ship_env import ShipEnv

env = ShipEnv()
# env = DummyVecEnv([lambda: env_])  # The algorithms require a vectorized environment to run

# model = PPO2(MlpPolicy, env, verbose=1)
# model.learn(total_timesteps=1)

np.set_printoptions(suppress=True)

obs = env.reset()
for i in range(10):
    # action, _states = model.predict(obs)
    obs, reward, done, info = env.step(1)

    if done:
        env.reset()

    print("-"*20)
    print("obs = \t", obs)
    print("reward = \t", reward)
    print("done = \t", done)
    print("-"*20)

    time.sleep(0.1)


    # env.render()