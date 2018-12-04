import sys
from collections import deque

import numpy as np

from gym import Env
from gym.spaces import Discrete, Box
from gym.utils import seeding

# Plus self, other ships and goal position times 2 for x and y coordinates, times history size
from pymunk import Vec2d

from ship_gym.curriculum import Curriculum

DEFAULT_STATE_VAL = -1

STEP_PENALTY = -0.01

class ShipEnv(Env):

    metadata = {'render.modes': ['human', 'rgb_array']}
    action_space = Discrete(5)
    reward_range = (-1, 1)

    def __del__(self):
        print("Delete ShipEnv")

    # TODO: Derive the discrete actions
    def __init__(self, ship_game, config, max_steps=1000, history_size=2, n_ship_track=0, map=None):

        # TODO: Should add some basic sanity checks (max_steps > 0 etc.)
        self.last_action = None
        self.max_steps = max_steps
        self.last_action = None
        self.reward = 0
        self.cumulative_reward = 0
        self.step_count = 0
        self.game = ship_game

        self.config = config
        self.episodes_count = -1 # Because the first reset will increment it to 0

        # TODO: This is a mess of too many parameters and poorly named ones
        self.n_ship_track = n_ship_track
        self.history_size = history_size
        self.n_states = (self.n_ship_track + 1 + 1) * 2 + 1 + 1
        self.states_history = self.n_states * self.history_size
        if self.n_ship_track < 0:
            raise ValueError("n_ship_track must be non-negative")
        if self.history_size < 1:
            raise ValueError("history_size must be greater than zero")
        if len(self.game.ships) > self.n_ship_track:
            print("* WARNING * There are more ships in the self.game than can be stored by this ship_gym configuration. "
                  "You should increase the N_SHIP_POSITIONS")
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
            # if len(self.game.goals) <= 5:
                # print(f"LAST 5 GOALS : GOAL #{self.game.total_goals - len(self.game.goals)} / {self.game.total_goals} REACHED")
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

        Px Py R Gx Gy S1x S1y S2x S2y S3x S3y ... SNx SNy

        Where
        P is the player position
        A is the player angle
        R is the rudder angle
        G is the goal position
        S are the ship positions
        N is the number of ships its tracking


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

        ship_positions = []
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
            print("ALL GOALS REACHED! -- CUM REWARD = ", self.cumulative_reward)
            return True

        player = self.game.player
        if player.x < 0 or player.x > self.game.bounds[0]:
            # print("X out of bounds")
            return True
        elif player.y < 0 or player.y > self.game.bounds[1]:
            # print("Y out of bounds")
            return True

        if self.step_count >= self.max_steps:
            print("MAX STEPS")
            return True

        return False

    def check_curriculum(self):
        # See which ones are curriculum

        currs = [v for k,v in self.config.items() if isinstance(v, Curriculum)]
        for c in currs:

            if c.progress(self.cumulative_reward):
                print("\n***\n New lesson = ", c.lesson, "\n***\n")

                # print(int)


        # Easy non generic implementation
        # exp_reward = 0.9 * self.n_goals - self.n_obstacles * 0.4
        # exp_reward = 0
        #
        # if self.cumulative_reward > exp_reward:
        # 	print("Training progressed!")
        # 	self.lesson += 1
        #
        # 	if self.lesson < 5:
        # 		self.n_goals += 1
        # 	else:
        # 		self.n_obstacles += 1


        # if self.curriculum is None:
        # 	return
        #
        # else:
        # 	if self.curriculum.progress(self)
        # 	for param in self.curriculum.param_names:
        # 		try:
        # 			self[]



    def step(self, action):
        assert self.action_space.contains(action), "%r (%s) invalid" % (action, type(action))

        # print("Step #", self.step_count)

        self.game.handle_action(action)
        self.game.update()
        self.game.render()

        self.determine_reward()
        self.cumulative_reward += self.reward
        self.__add_states()
        self.step_count += 1

        done = self.is_done()

        return np.array(self.states), self.reward, done, {}

    def render(self, mode='human', close=False):
        print("ShipEnv Render ...")
        out = sys.stdout

        if self.last_action is not None:
            out.write(f'action={self.last_action}, cum_reward={self.cumulative_reward}')

        return

    def setup_goals(self):
        # self.generate_uniform_random_goals()

        # HACK: TODO: I do the int because it can be a curriculum. Should figure out a better way ...
        self.gen_goal_path(int(self.config["n_goals"]))

    def setup_obstacles(self):
        pass

    def setup_player(self):
        x = np.random.randint(15, self.game.bounds[0])
        y = np.random.randint(5, 15)

        self.game.player.body.position = Vec2d(x,y)


    def setup_game_env(self):
        self.setup_player()
        self.setup_goals()
        self.setup_obstacles()


    def gen_goal_path(self, n):

        x = self.game.player.x
        y = self.game.player.y + 50

        x_end = np.random.randint(30, self.game.bounds[0] - 30)
        y_end = np.random.randint(self.game.bounds[1] - 60, self.game.bounds[1] - 30)

        max_n = 5
        x_delta = (x_end - x) / max_n
        y_delta = (y_end - y) / max_n

        jitter = 20

        for i in range(1, n+1):
            gx = x + x_delta * i + np.random.randint(-jitter, jitter)
            gy = y + y_delta * i + np.random.randint(-jitter, jitter)
            self.game.add_goal(gx, gy)

    def reset(self):
        self.game.reset()
        self.check_curriculum()

        self.last_action = None
        self.reward = 0
        self.cumulative_reward = 0
        self.step_count = 0
        self.episodes_count += 1
        n = self.n_states * self.history_size
        self.states = deque([DEFAULT_STATE_VAL] * n, maxlen=n)

        self.setup_game_env()
        self.__add_states()

        return np.array(self.states)


if __name__ == '__main__':

    pass