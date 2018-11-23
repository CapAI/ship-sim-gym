import os
import time

import gym
import numpy as np
from baselines.results_plotter import ts2xy
from stable_baselines.bench import load_results, Monitor
from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2

from ship_gym.ship_env import ShipEnv

log_dir = "/Users/gerard/Desktop/learning/"

best_mean_reward = -np.inf
n_steps = 0

log_step_interval = 100

def callback(_locals, _globals):
    """
    Callback called at each step (for DQN an others) or after n steps (see ACER or PPO2)
    :param _locals: (dict)
    :param _globals: (dict)
    """
    global n_steps, best_mean_reward
    # Print stats every 1000 calls
    # print(1/0)
    if (n_steps + 1) % log_step_interval == 0:
        # Evaluate policy performance
        x, y = ts2xy(load_results(log_dir), 'timesteps')
        if len(x) > 0:
            mean_reward = np.mean(y[-100:])
            print(x[-1], 'timesteps')
            print("Best mean reward: {:.2f} - Last mean reward per episode: {:.2f}".format(best_mean_reward, mean_reward))

            # New best model, you could save the agent here
            if mean_reward > best_mean_reward:
                best_mean_reward = mean_reward
                # Example for saving best model
                print("Saving new best model")
                _locals['self'].save(log_dir + 'best_model.pkl')
    n_steps += 1
    return False

env = ShipEnv(fps=100, speed=10)
# env = gym.make('CartPole-v0')
env = Monitor(env, log_dir, allow_early_resets=True)
env = DummyVecEnv([lambda: env])  # The algorithms require a vectorized environment to run

np.set_printoptions(suppress=True)

model = PPO2(MlpPolicy, env, verbose=0, tensorboard_log=os.path.join(log_dir, "tensorboard"))
model.learn(total_timesteps=100000, callback=callback)
model.save("result")

# obs = env.reset()
# for i in range(10):
#     # action, _states = model.predict(obs)
#     action = 0
#     obs, reward, done, info = env.step(action)
#
#     if done:
#         obs = env.reset()
#
#     print("-" * 20)
#     print("obs = \t", obs)
#     print("reward = \t", reward)
#     print("done = \t", done)
#     print("-" * 20)

    # ship_gym.render()