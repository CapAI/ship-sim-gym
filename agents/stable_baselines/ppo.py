import os
import time

import gym
import numpy as np
from baselines.results_plotter import ts2xy
from stable_baselines.bench import load_results, Monitor
from stable_baselines.common import set_global_seeds
from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines import PPO2

import time

from ship_gym.game import ShipGame
from ship_gym.ship_env import ShipEnv

log_dir = os.path.expanduser('~/Desktop/learning')
model_dir = os.path.join(log_dir, "models")

os.makedirs(model_dir, exist_ok=True)

best_mean_reward = -np.inf
n_steps = 0

log_step_interval = 100

t_last = time.time()


def callback(_locals, _globals):
    """
    Callback called at each step (for DQN an others) or after n steps (see ACER or PPO2)
    :param _locals: (dict)
    :param _globals: (dict)
    """
    global n_steps, best_mean_reward, t_last
    # Print stats every 1000 calls
    t = time.time()

    if (n_steps + 1) % log_step_interval == 0:
        # Evaluate policy performance
        x, y = ts2xy(load_results(log_dir), 'timesteps')
        if len(x) > 0:
            mean_reward = np.mean(y[-100:])
            print(x[-1], 'timesteps')
            print(
                "Best mean reward: {:.2f} - Last mean reward per episode: {:.2f}".format(best_mean_reward, mean_reward))

            # t_delta = t - t_last
            # pace = log_step_interval / t_delta
            # t_last = t

            # print("Pace=", pace)

            # New best model, you could save the agent here
            if mean_reward > best_mean_reward:
                best_mean_reward = mean_reward
                # Example for saving best model
                print("Saving new best model")
                _locals['self'].save(log_dir + 'best_model.pkl')
    n_steps += 1
    return False


game_fps = 1000
game_speed = 30

bounds = (1000,1000)


# env = ShipEnv(fps=10000, speed=20)

# Setting it to the number of CPU's you have is usually optimal
num_cpu = 1

np.set_printoptions(suppress=True)

tb_root_dir = os.path.join(log_dir, f"tensorboard_{int(time.time())}")

''' SET UP YOUR HYPERPARAMETERS HERE'''

lrs = [1.0e-5, 1.0e-4, 1.0e-3]

max_goals = 10
max_steps = int(1e6)

def get_model_path(n_goals, lr):
    return os.path.join(model_dir, f"result_g{n_goals}_lr{lr}")

for n_goal in range(1, max_goals):

    def make_env(rank, n_goals, seed=0):
        """
        Utility function for multiprocessed env.

        :param n_goals:
        :param env_id: (str) the environment ID
        :param num_env: (int) the number of environment you wish to have in subprocesses
        :param seed: (int) the inital seed for RNG
        :param rank: (int) index of the subprocess
        """

        def _init():
            env = ShipEnv(ShipGame(fps=game_fps, speed=game_speed, bounds=bounds), max_steps=max_steps, n_goals=n_goals)
            env.seed(seed + rank)
            # env = Monitor(env, log_dir, allow_early_resets=True)

            return env

        set_global_seeds(seed)
        return _init

    for lr in lrs:
        start_t = time.time()

        env = SubprocVecEnv([make_env(i, n_goal) for i in range(num_cpu)])

        tb_dir = os.path.join(tb_root_dir, f"ppo2_lr{lr}_g{n_goal}")
        model = PPO2(MlpPolicy, env, learning_rate=lr, verbose=0, tensorboard_log=tb_dir)

        if n_goal > 1:
            # Previous model?

            path = get_model_path(n_goal-1, lr)
            model.load(path)

        model.learn(total_timesteps=max_steps / n_goal, log_interval=1000)

        end_t = time.time()
        elapsed = end_t - start_t
        print(f"Trained {n_steps} steps in {elapsed} seconds")
        print(f"Speed = {n_steps / (elapsed / 60)} steps/min")

        path = get_model_path(n_goal, lr)
        model.save(path)
