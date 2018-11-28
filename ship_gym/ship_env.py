import sys
from collections import deque

import numpy as np

from gym import Env
from gym.spaces import Discrete, Box
from gym.utils import seeding

# Plus self, other ships and goal position times 2 for x and y coordinates, times history size
from pymunk import Vec2d

DEFAULT_STATE_VAL = -1

STEP_PENALTY = -0.01

class ShipEnv(Env):

    metadata = {'render.modes': ['human', 'rgb_array']}
    action_space = Discrete(5)
    reward_range = (-1, 1)

    def __del__(self):
    	print("Delete shipenv")

    # TODO: Derive the discrete actions
    def __init__(self, ship_game, max_steps=200, n_ship_track=2, history_size=2, n_goals=0, goal_gen='random'):
        if n_ship_track < 0:
            raise ValueError("n_ship_track must be non-negative")
        if history_size < 1:
            raise ValueError("history_size must be greater than zero")

        self.last_action = None
        self.max_steps = max_steps
        self.last_action = None
        self.reward = 0
        self.cumulative_reward = 0
        self.step_count = 0
        self.game = ship_game
        self.n_goals = n_goals

        self.n_ship_track = n_ship_track
        self.history_size = history_size
        self.n_states = (n_ship_track + 1 + 1) * 2
        self.states_history = self.n_states * history_size
        self.observation_space = Box(low=0, high=max(self.game.bounds), shape=(self.states_history,), dtype=np.uint8)

        # print(" *** SHIP-GYM INITIALIZED *** ")
       
    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)

        # Important to actually seed it!!! I thought above would work but it's not enough
        np.random.seed(seed)

        return [seed]

    def determine_reward(self):

        if self.game.colliding:
            self.reward = -1.0
        if self.game.goal_reached:
            self.reward = 1.0
        else:
            self.reward = STEP_PENALTY  # Small penalty

    def _normalized_coords(self, x, y):
        return x / self.game.bounds[0], y / self.game.bounds[1]

    def __add_states(self):
        '''
        Push back some new state information for the current timestep onto the FIFO queue for all history timesteps
        it keeps track of.

        Layout of a single time step state is like this:

        Px Py Gx Gy S1x S1y S2x S2y S3x S3y ... SNx SNy

        Where N is the number of ships its tracking

        :return:
        '''

        states = self.n_states * [-1]

        # Myself
        states[:2] = [self.game.player.x, self.game.player.y]
        goal = self.game.closest_goal()
        if goal:
            states[2:4] = [goal.body.position.x, goal.body.position.y]

        ship_positions = []
        # if len(self.game.ships) > self.n_ship_track:
        #     print("* WARNING * There are more ships in the self.game than can be stored by this ship_gym configuration. "
        #           "You should increase the N_SHIP_POSITIONS")

        for i in range(min(len(self.game.ships), self.n_ship_track)):
            #   TODO: Figure out the closest few if there are too few state slots available

            ship = self.game.ships[i]
            ship_positions.extend([ship.x, ship.y])


        states[4:4+len(ship_positions)] = ship_positions
        self.states.extend(states)

    def is_done(self):
        if self.game.colliding:
            # print("OOPS --- COLLISION")
            return True
        elif len(self.game.goals) == 0:
            print("YEAH --- ALL GOALS REACHED")
            return True

        # TODO: Untested x or y bounds because perfect square ...
        if self.game.player.x < 0 or self.game.player.x > self.game.bounds[0]:
            # print("X out of bounds")
            return True
        elif self.game.player.y < 0 or self.game.player.y > self.game.bounds[1]:
            # print("Y out of bounds")
            return True

        if self.step_count >= self.max_steps:
            print("MAX STEPS")
            return True

        return False


    def step(self, action):
        assert self.action_space.contains(action), "%r (%s) invalid" % (action, type(action))

        # print("Step #", self.step_count)

        self.game.handle_action(action)
        self.game.update()
        self.game.render()

        self.determine_reward()
        self.__add_states()
        self.step_count += 1

        done = self.is_done()

        return np.array(self.states), self.reward, done, {}

    def render(self, mode='human', close=False):
        print("ShipEnv Render ...")
        out = sys.stdout

        if self.last_action is not None:
            out.write(f'action={self.last_action}, reward={self.last_reward}')

        return out

    def generate_uniform_random_goals(self):

        i = 0
        while i < self.n_goals:
            x = np.random.randint(30, self.game.bounds[0] - 30)
            y = np.random.randint(30, self.game.bounds[1] - 30)
            xy_pos = Vec2d(x, y)

            if xy_pos.get_distance(self.game.player.body.position) > 20:
                i += 1
                self.game.add_goal(x, y)

    def reset(self, spawn_point=(10,10)):
        self.game.reset(spawn_point=spawn_point)
        self.generate_uniform_random_goals()
        self.last_action = None
        self.reward = 0
        self.cumulative_reward = 0
        self.step_count = 0

        n = self.n_states * self.history_size
        self.states = deque([DEFAULT_STATE_VAL] * n, maxlen=n)
        self.__add_states()

        return np.array(self.states)


if __name__ == '__main__':

    pass