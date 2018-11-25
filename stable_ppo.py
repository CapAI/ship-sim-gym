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
			print("Best mean reward: {:.2f} - Last mean reward per episode: {:.2f}".format(best_mean_reward, mean_reward))

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


game_fps=1000
game_speed=30
max_steps=1000

def make_env(rank, seed=0):
	"""
	Utility function for multiprocessed env.

	:param env_id: (str) the environment ID
	:param num_env: (int) the number of environment you wish to have in subprocesses
	:param seed: (int) the inital seed for RNG
	:param rank: (int) index of the subprocess
	"""

	def _init():
		env = ShipEnv(fps=game_fps, speed=game_speed, max_steps=max_steps)
		env.seed(seed + rank)
		# env = Monitor(env, log_dir, allow_early_resets=True)

		# Place window
		x = rank % 4 * 500
		y = rank % 2 * 500

		# os.environ['SDL_VIDEO_WINDOW_POS'] = str(x) + "," + str(y)

		return env

	set_global_seeds(seed)
	return _init

# env = ShipEnv(fps=10000, speed=20)

# Setting it to the number of CPU's you have is usually optimal
num_cpu = 8
env = SubprocVecEnv([make_env(i) for i in range(num_cpu)])
# 
# env = DummyVecEnv([lambda: env])  # The algorithms require a vectorized environment to run

np.set_printoptions(suppress=True)

tb_root_dir = os.path.join(log_dir, f"tensorboard_{int(time.time())}")

''' SET UP YOUR HYPERPARAMETERS HERE'''
# lrs = [1.0e-6, 1.0e-5, 1.0e-4, 1.0e-3, 1.0e-2]
lrs = [1.0e-5, 1.0e-4, 1.0e-3]
# lrs = [1.0e-5, 1.0e-4, 1.0e-3]
n_steps = int(1e6)

for i in range(3):
	for lr in lrs:
		
		start_t = time.time()

		tb_dir = os.path.join(tb_root_dir, f"ppo2_{i}_lr={lr}")
		model = PPO2(MlpPolicy, env, learning_rate=lr, verbose=0, tensorboard_log=tb_dir)
		# model.learn(total_timesteps=n_steps, callback=callback)
		model.learn(total_timesteps=n_steps)
		model.save(os.path.join(model_dir, "result_" + str(lr)))

		end_t = time.time()
		elapsed = end_t - start_t
		print(f"Trained {n_steps} steps in {elapsed} seconds")
		print(f"Speed = {n_steps / (elapsed / 60)} steps/min")
