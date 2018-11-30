import os
import time
import sys

import gym
import numpy as np
from baselines.results_plotter import ts2xy
from stable_baselines.bench import load_results, Monitor
from stable_baselines.common import set_global_seeds
from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines import PPO2, ACER

from ship_gym.game import ShipGame
from ship_gym.ship_env import ShipEnv
from datetime import datetime

from tqdm import tqdm


log_dir = "logs/learning"
model_dir = "models"

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

def make_env(rank, bounds, game_fps, game_speed, max_steps, seed=0):
		"""
		Utility function for multiprocessed env.

		:param n_goals:
		:param env_id: (str) the environment ID
		:param num_env: (int) the number of environment you wish to have in subprocesses
		:param seed: (int) the inital seed for RNG
		:param rank: (int) index of the subprocess
		"""

		def _init():
			env = ShipEnv(ShipGame(fps=game_fps, speed=game_speed, bounds=bounds), max_steps=max_steps)
			env.seed(seed + rank)
			# env = Monitor(env, log_dir, allow_early_resets=True)

			return env

		set_global_seeds(seed)
		return _init

def get_model_path(n_goals, lr, n_obstacles=0):
	return os.path.join(model_dir, f"result_g{n_goals}_o{n_obstacles}_lr{lr}")


tb_root_dir = os.path.join(log_dir, "tb", str(int(time.time())))

def train(model_cls, tid, env, n_goal, n_obstacles, lr, steps):

	start_t = time.time()
	tb_dir = os.path.join(tb_root_dir, f"{tid}_{model_cls.__name__}_g{n_goal}_o{n_obstacles}")
	# model = PPO2(MlpPolicy, env, learning_rate=lr, verbose=0, tensorboard_log=tb_dir)
	model = model_cls(MlpPolicy, env, learning_rate=lr, verbose=1, tensorboard_log=tb_dir)

	if n_goal > 1:
		# Previous model?

		path = get_model_path(n_goal-1, lr)

		try:
			model.load(path)
		except ValueError as e:
			print(f"WARNING: Could not find model 'path'")
			sleep(0.5)

		print(f"Model '{path}' loaded!")

	model.learn(total_timesteps=steps, log_interval=10000)

	end_t = time.time()
	elapsed = end_t - start_t

	print(f"Trained {steps} steps in {elapsed} seconds")
	print(f"Speed = {steps / (elapsed / 60)} steps/min")
	print()

	path = get_model_path(n_goal, lr)
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
	# noptepochs = [3, 5, 7]
	# mini_batches

	max_goals = 5
	max_steps = 1000

	game_fps = 10000
	game_speed = 10
	bounds = (800,800)

	# Setting it to the number of CPU's you have is usually optimal
	num_cpu = 8
	n_obstacles = 0
	total_train_steps = 1e6

	env = SubprocVecEnv([make_env(i, bounds, game_fps, game_speed, max_steps) for i in range(num_cpu)])
	i = 0
	for n_goal in tqdm(range(1, max_goals+1)):
		# Update envs to use the right number of goals. <3 this function
		env.set_attr('n_goals', n_goal)
		steps = int(total_train_steps / max_goals)

		for lr in lrs:
			print(f"""
Started training at {datetime.now()}
------------------------------------------------
Training Steps 	:\t {steps} / {max_steps}
Number of goals :\t {n_goal} / {max_goals}
Learning rate   :\t {lr} 
			""")

			i += 1
			train(PPO2, i, env, n_goal, 0, lr, steps)
			# train(ACER, env, n_goals, 0, lr, steps)

	print("*" * 30)
	print(" "*10,"     DONE!     ", " "*10)
	print(" ", datetime.now(), " ")
	print("*" * 30)

	del env

	sys.exit(0)





if __name__ == '__main__':
	main()