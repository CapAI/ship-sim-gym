import sys
from collections import deque

import numpy as np

from gym import Env
from gym.spaces import Box
from gym.utils import seeding

from ship_gym.game import ShipGame

DEFAULT_STATE_VAL = -1
STEP_PENALTY = -0.01


class ShipEnv(Env):

    metadata = {'render.modes': ['human', 'rgb_array']}
    action_space = Box(low=0, high=1, shape=(2,), dtype=np.float16)
    reward_range = (-1, 1)

    # TODO: Derive the discrete actions
    def __init__(self, game_config, env_config):

        # TODO: Should add some basic sanity checks (max_steps > 0 etc.)
        self.last_action = None
        self.reward = 0
        self.cumulative_reward = 0
        self.step_count = 0
        self.env_config = env_config

        self.game = ShipGame(game_config)
        self.episodes_count = -1 # Because the first reset will increment it to 0


        """P is the player position
        A is the player angle
        R is the rudder angle
        G is the nearest goal position
        L are the lidar values
        N is the number of rays lidar uses
        """
        self.n_states = 2 + 1 + 1 + 2 + self.game.player.lidar.n_beams
        self.states_history = self.n_states * self.env_config.HISTORY_SIZE

        if self.env_config.HISTORY_SIZE < 1:
            raise ValueError("history_size must be greater than zero")
        self.observation_space = Box(low=0, high=max(self.game.bounds), shape=(self.states_history,), dtype=np.uint8)

        # print(" *** SHIP-GYM INITIALIZED *** ")

    def seed(self, seed=None):
        """
        Seed numpy random generator
        :param seed: the seed to use
        """
        self.np_random, seed = seeding.np_random(seed)
        # Important to actually seed it!!! I thought above would work but it's not enough
        np.random.seed(seed)
        return [seed]

    def determine_reward(self):
        """
        Determines the reward of the current timestep
        """
        if self.game.colliding:
            self.reward = -1.0
        if self.game.goal_reached:
            self.reward = 1.0

        # TODO: Code duplication with is_done()
        elif self.game.player.x < 0 or self.game.player.x > self.game.bounds[0]:
            self.reward = -1
        elif self.game.player.y < 0 or self.game.player.y > self.game.bounds[1]:
            self.reward = -1
        else:
            self.reward = STEP_PENALTY  # Small penalty

    def __add_states(self):
        '''
        Push back some new state information for the current timestep onto the FIFO queue for all history timesteps
        it keeps track of.

        Layout of a single time step state is like this:

        Px Py R Gx Gy L1 L2 ... Ln

        Where
        P is the player position
        A is the player angle
        R is the rudder angle
        G is the nearest goal position
        L are the lidar values
        N is the number of rays lidar uses


        :return: the complete history buffer of states extended with the most recent one
        '''

        states = self.n_states * [-1]

        # Myself
        goal = self.game.closest_goal()
        goal_pos = [-1, -1]
        player = self.game.player

        if goal:
            goal_pos = [goal.body.position.x, goal.body.position.y]
        states[:6] = [player.x, player.y, player.rudder_angle, player.body.angle, goal_pos[0], goal_pos[1]]

        lidar_vals = self.game.player.lidar.vals

        states[6:] = lidar_vals
        self.states.extend(states)

    def is_done(self):
        """
        Determines whether the episode has finished based on collisions and goals reached.
        :return:
        """
        if self.game.colliding:
            return True
        elif len(self.game.goals) == 0:
            return True

        player = self.game.player
        if player.x < 0 or player.x > self.game.bounds[0]:
            return True
        elif player.y < 0 or player.y > self.game.bounds[1]:
            return True

        if self.step_count >= self.env_config.MAX_STEPS:
            return True

        return False

    def step(self, action):
        """

        :param action:
        :return:
        """
        if isinstance(self.action_space, Box):
            lb = self.action_space.low
            ub = self.action_space.high
            scaled_action = lb + (action + 1.) * 0.5 * (ub - lb)
            scaled_action = np.clip(scaled_action, lb, ub)
            self.game.handle_cont_action(scaled_action)
        else:
            assert self.action_space.contains(action), "%r (%s) invalid" % (action, type(action))
            self.game.handle_discrete_action(action)

        self.game.update()
        self.game.render()

        self.determine_reward()
        self.cumulative_reward += self.reward
        self.__add_states()
        self.step_count += 1

        done = self.is_done()

        return np.array(self.states), self.reward, done, {}

    def render(self, mode='human', close=False):
        """
        Display additional debug information about the state of the environment here. You might also render actual images
        or videos from the game's frame buffer (not currently implemented)
        :param mode: the display mode, currently ignored but might be use to visualise different ways
        :param close: Whether to close the environment. Also ignored in the current version
        """
        out = sys.stdout

        if self.last_action is not None:
            out.write(f'action={self.last_action}, cumm_reward={self.cumulative_reward}')


    def reset(self):
        self.game.reset()
        self.last_action = None
        self.reward = 0
        self.cumulative_reward = 0
        self.step_count = 0
        self.episodes_count += 1

        # Setup states
        n = self.n_states * self.env_config.HISTORY_SIZE
        self.states = deque([DEFAULT_STATE_VAL] * n, maxlen=n)
        self.__add_states()

        return np.array(self.states)
