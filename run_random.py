import gym
import ship_gym

env = gym.make('ShipSim-v0')

env.reset()
for _ in range(1000):
    env.render()
    ret = env.step(env.action_space.sample()) # take a random action

    print(ret)