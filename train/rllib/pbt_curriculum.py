# Postprocess the perturbed config to ensure it's still valid
import random
from pprint import pprint

import ray
import ray.tune as tune
from ray.rllib.agents.ppo import PPOAgent
from ray.tune import run_experiments, register_env

from ray.tune.schedulers import PopulationBasedTraining

from ship_gym.curriculum import Curriculum
from ship_gym.game import ShipGame
from ship_gym.ship_env import ShipEnv

if __name__ == '__main__':


    def on_episode_start(info):
        print(info.keys())  # -> "env", 'episode"
        episode = info["episode"]
        print("episode {} started".format(episode.episode_id))
        # episode.user_data["pole_angles"] = []

    def on_episode_step(info):
        episode = info["episode"]
        pole_angle = abs(episode.last_observation_for()[2])
        episode.user_data["pole_angles"].append(pole_angle)

    def on_episode_end(info):
        episode = info["episode"]
        print("Episode End")
        # mean_pole_angle = np.mean(episode.user_data["pole_angles"])
        # print("episode {} ended with length {} and pole angles {}".format(
        #     episode.episode_id, episode.length, mean_pole_angle))
        # episode.custom_metrics["mean_pole_angle"] = mean_pole_angle


    def env_creator(env_config):
        game = ShipGame(speed=20, fps=10000, bounds=(800, 800))
        env = ShipEnv(game, env_config, n_ship_track=5)

        return env


    register_env("ShipGym-v1", env_creator)


    def on_train_result(info):
        # print(info.keys())  # -> "env", 'episode"
        pprint(info)
        result = info["result"]
        reward = result["episode_reward_mean"]
        print("Reward = ", reward)
        if reward > 200:
            phase = 2
        elif result["episode_reward_mean"] > 100:
            phase = 1
        else:
            phase = 0
        agent = info["agent"]
        agent.optimizer.foreach_evaluator(lambda ev: ev.env.set_phase(phase))


    pbt = PopulationBasedTraining(
        time_attr="time_total_s",
        reward_attr="episode_reward_mean",
        perturbation_interval=60 * 30,
        resample_probability=0.25,

        # Specifies the mutations of these hyperparams
        hyperparam_mutations={
            "lambda": lambda: random.uniform(0.9, 1.0),
            "clip_param": lambda: random.uniform(0.01, 0.5),
            "lr": [1e-3, 5e-4, 1e-4, 5e-5, 1e-5],
            "num_sgd_iter": lambda: random.randint(1, 30),
            "sgd_minibatch_size": lambda: random.randint(128, 16384),
            "train_batch_size": lambda: random.randint(2000, 160000),
        })


    def train(config, reporter):
        agent = PPOAgent(config=config, env="ShipGym-v1")

        while True:
            print("Training ....... ")
            result = agent.train()
            print("Train done ... ")
            pprint(result)
            reporter(**result)
            if result["episode_reward_mean"] > 0:
                print("Phase #1")
                phase = 2
            elif result["episode_reward_mean"] > 100:
                # print("Phase #2")
                phase = 1
            else:
                phase = 0
            agent.optimizer.foreach_evaluator(lambda ev: ev.env.set_phase(phase))

    ray.init(num_cpus=8, num_gpus=1)

    n_goals = 5
    reward_done = .9 * n_goals

    run_experiments(
        {
            "pbt_ship_sim": {
                "run": "PPO",
                # "run": train,
                "env": "ShipGym-v1",
                "num_samples": 28,  # Repeat the experiment this many times
                "checkpoint_at_end": True,
                "checkpoint_freq": 10,
                "config": {
                    "env_config": {
                        "n_goals": Curriculum([1, 2, 3, 4, 5], [0.9, 1.8, 2.75, 3.7], repeat_condition=100),
                    },
                    "kl_coeff": 1.0,
                    "num_workers": 7,
                    "num_gpus": 1,

                    # These params are tuned from a fixed starting value.
                    "lambda": 0.95,
                    "clip_param": 0.2,

                    # These params start off randomly drawn from a set.
                    "lr":
                        lambda spec: random.choice([1e-3, 5e-4, 1e-4, 5e-5, 1e-5]),
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