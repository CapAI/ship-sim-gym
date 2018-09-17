from baselines import deepq

import gym
import ship_gym

def main():
    # env = UnityEnv("./envs/GridWorld", 0, use_visual=True)


    env = gym.make('ShipSim-v0')
    model = deepq.models.cnn_to_mlp(
        convs=[(32, 8, 4), (64, 4, 2), (64, 3, 1)],
        hiddens=[256],
        dueling=True,
        num_actions=5,
        scope="dunno"
    )
    act = deepq.learn(
        env,
        model,
        lr=1e-3,
        max_timesteps=100000,
        buffer_size=50000,
        exploration_fraction=0.1,
        exploration_final_eps=0.02,
        print_freq=10,
    )

if __name__ == '__main__':
    main()