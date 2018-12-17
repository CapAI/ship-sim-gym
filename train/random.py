from ship_gym.ship_env import ShipEnv
from ship_gym.config import EnvConfig, GameConfig

gc = GameConfig
gc.DEBUG = True
gc.SPEED = 1
gc.FPS = 30

env = ShipEnv(game_config=gc, env_config=EnvConfig)

env.reset()
cont = True

for _ in range(1000):

    total_reward = 0
    for _ in range(100):
        env.render()

        ret = env.step(env.action_space.sample())  # take a random action
        print(ret)

        total_reward += ret[1]
        if ret[2] == True:
            print(f"AGENT IS DONE. TOTAL REWARD = {total_reward}")
            env.reset()
            break
