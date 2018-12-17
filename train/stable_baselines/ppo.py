import multiprocessing
import os
import time
import sys

import numpy as np
from baselines.results_plotter import ts2xy
from stable_baselines.bench import load_results, Monitor
from stable_baselines.common import set_global_seeds
from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines import PPO2, ACER

from ship_gym.config import EnvConfig, GameConfig
from ship_gym.ship_env import ShipEnv
from datetime import datetime

from tqdm import tqdm


log_dir = "logs/learning"
model_dir = "models"
log_step_interval = 10000

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

            # New best model, you could save the agent here
            if mean_reward > best_mean_reward:
                best_mean_reward = mean_reward
                # Example for saving best model
                print("Saving new best model")
                _locals['self'].save(log_dir + 'best_model.pkl')
    n_steps += 1
    return False

def make_env():
        """
        Utility function for multiprocessed env.

        :param n_goals:
        :param env_id: (str) the environment ID
        :param num_env: (int) the number of environment you wish to have in subprocesses
        :param seed: (int) the inital seed for RNG
        :param rank: (int) index of the subprocess
        """

        game_config = GameConfig
        game_config.FPS = 1000
        game_config.SPEED = 30
        game_config.DEBUG = True # This will render more primitives to make it more observable for humans (you), although this is not necessary for training and incurs a small performance hit
        game_config.BOUNDS = (1000, 1000)

        def _init():
            env_config = EnvConfig
            env = ShipEnv(game_config, env_config)
            return env

        return _init

def get_model_path(lr):
    return os.path.join(model_dir, f"result_lr{lr}")


tb_root_dir = os.path.join(log_dir, "tb", str(int(time.time())))

def train(model_cls, tid, env, lr, steps):

    start_t = time.time()
    tb_dir = os.path.join(tb_root_dir, f"{tid}_{model_cls.__name__}")
    model = model_cls(MlpPolicy, env, learning_rate=lr, verbose=1, tensorboard_log=tb_dir)

    model.learn(total_timesteps=steps, log_interval=10000)

    end_t = time.time()
    elapsed = end_t - start_t

    print(f"Trained {steps} steps in {elapsed} seconds")
    print(f"Speed = {steps / (elapsed / 60)} steps/min")
    print()

    path = get_model_path(lr)
    model.save(path)

def main():

    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(model_dir, exist_ok=True)

    np.set_printoptions(suppress=True)

    ''' SET UP YOUR (HYPER)PARAMETERS HERE'''

    def make_lr_func(start, stop):

        def lr_func(frac):
            return start + (stop - start) * (1-frac)

        return lr_func

    lrs = [1.0e-3, 1.0e-4, 1.0e-5]
    lrs = [make_lr_func(s, 0) for s in lrs]

    # Setting it to the number of CPU's you have is usually optimal
    num_cpu = multiprocessing.cpu_count()
    env = SubprocVecEnv([make_env() for i in range(num_cpu)])

    i = 0
    steps = int(1e6)

    for lr in lrs:
        print(f"""
Started training at {datetime.now()}
------------------------------------------------
Training Steps 	:\t {steps}
Learning rate   :\t {lr} 
            """)

        i += 1
        train(PPO2, i, env, lr, steps)
        # train(ACER, env, n_goals, 0, lr, steps)

    print("*" * 30)
    print(" "*10,"     DONE!     ", " "*10)
    print(" ", datetime.now(), " ")
    print("*" * 30)


if __name__ == '__main__':
    main()