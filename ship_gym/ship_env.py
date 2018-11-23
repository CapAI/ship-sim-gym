import sys

import numpy as np

from gym import Env
from gym.spaces import Discrete, Box
from gym.utils import seeding

from ship_gym import game

N_SHIP_POSITIONS = 4
HISTORY_SIZE = 1

# Plus self, other ships and goal position times 2 for x and y coordinates, times history size
N_STATES = (N_SHIP_POSITIONS + 1 + 1) * 2 * HISTORY_SIZE
print(N_STATES)

class ShipEnv(Env):

    metadata = {'render.modes': ['human', 'rgb_array']}
    action_space = Discrete(5)
    reward_range = (-1, 1)

    observation_space = Box(low=0, high=255, shape=(N_STATES,), dtype=np.uint8)
    # observation_space = Box(low=0, high=255, shape=(STATE_H, STATE_W, 3), dtype=np.uint8)

    # TODO: Derive the discrete actions
    def __init__(self, max_steps=1000, speed=1, fps=30):
        self.last_action = None
        self.max_steps = max_steps
        self.last_action = None
        self.reward = 0
        self.cumulative_reward = 0
        self.step_count = 0

        game.init(_speed=speed, _fps=fps)

        print(" *** SHIP-GYM INITIALIZED *** ")
       
    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def determine_reward(self):

        if game.colliding:
            self.reward = -1.0
        if game.goal_reached:
            self.reward = 1.0
        else:
            self.reward = -0.01  # Small penalty

    def set_states(self):
        self.states = N_STATES * [-1]

        # Myself
        self.states[:2] = [game.player.x, game.player.y]
        goal = game.closest_goal()
        if goal:
            self.states[2:4] = [goal.body.position.x, goal.body.position.x]

        ship_positions = []
        if len(game.ships) > N_SHIP_POSITIONS:
            print("* WARNING * There are more ships in the game than can be stored by this ship_gym configuration. "
                  "You should increase the N_SHIP_POSITIONS")

        for i in range(min(len(game.ships), N_SHIP_POSITIONS)):
            #   TODO: Figure out the closest few if there are too few state slots available

            ship = game.ships[i]
            ship_positions.extend([ship.x, ship.y])


        self.states[4:4+len(ship_positions)] = ship_positions

    def is_done(self):
        if game.colliding:
            print("OOPS --- COLLISION")
            return True
        elif len(game.goals) == 0:
            print("YEAH --- ALL GOALS REACHED")
            return True

        # TODO: Untested x or y bounds because perfect square ...
        if game.player.x < 0 or game.player.x > game.bounds[0]:
            print("X out of bounds")
            return True
        elif game.player.y < 0 or game.player.y > game.bounds[1]:
            print("Y out of bounds")
            return True




    def step(self, action):
        assert self.action_space.contains(action), "%r (%s) invalid" % (action, type(action))

        # print("Step #", self.step_count)

        game.handle_action(action)
        game.update()
        game.render() # Also does the actual game progression

        self.determine_reward()
        self.set_states()
        self.step_count += 1

        done = self.is_done()

        return np.array(self.states), self.reward, done, {}

    def render(self, mode='human', close=False):
        print("ShipEnv Render ...")
        out = sys.stdout

        if self.last_action is not None:
            out.write(f'action={self.last_action}, reward={self.last_reward}')

        return out

    def reset(self):
        print("ShipEnv Reset")
        game.reset()

        self.last_action = None
        self.reward = 0
        self.cumulative_reward = 0
        self.step_count = 0
        self.set_states()

        return np.array(self.states)


if __name__ == '__main__':

    pass