import os
import random
import sys
import time

import numpy as np
import pygame

from pymunk import Vec2d, Transform
import pymunk as pm
import pymunk.pygame_util

from ship_gym import game_map
from ship_gym.config import GameConfig
from ship_gym.models import GameObject, Ship, PolyEnv, LiDAR

N_GOALS = 5
DEFAULT_BOUNDS = (500, 500)


class ShipGame(object):

    ships = list()
    goals = list()

    frame_counter = 0
    base_dt = 0.1
    colliding = False
    observe_mode = False
    record = False

    def __init__(self, game_config=None):

        if game_config is None:
            game_config = GameConfig

        self.speed = game_config.SPEED
        self.fps = game_config.FPS
        self.bounds = game_config.BOUNDS
        self.screen = pygame.display.set_mode(self.bounds)
        self.clock = pygame.time.Clock()
        self.goal_reached = False
        self.colliding = False

        self.debug_mode = game_config.DEBUG

        pygame.init()
        pygame.display.set_caption("Ship Sim Gym")
        pygame.key.set_repeat(10, 10)

        print("-"*30)
        print("SHIP GAME INITIALIZED")
        print("DEBUG MODE = ", self.debug_mode)
        print("GAME SPEED = ", self.speed)
        print("GAME FPS   = ", self.fps)
        print("-"*30, "\n")

        self.reset()

    def gen_level(self):
        """
        Generate a level on the fly by calling game map gen river poly function wrapping them in a GeoMap object
        and adding the generated pymunk primitives (shapes and bodies) to the game space
        :return:
        """
        poly = game_map.gen_river_poly(self.bounds)

        self.level = PolyEnv(poly, self.bounds)

        for body, shape in zip(self.level.bodies, self.level.shapes):
            self.space.add(body, shape)

    def invert_p(self, p):
        """Because in screen Y=0 is at the top or some shit like that """
        return Vec2d(p[0], self.bounds[1] - p[1])

    def add_goal(self, x, y):
        """Add a ball to the given space at a random position """
        self.total_goals += 1

        mass = 1
        radius = 5
        inertia = pm.moment_for_circle(mass, 0, radius, (0,0))
        body = pm.Body(mass, inertia)

        body.position = x, y
        shape = pm.Circle(body, radius, (0,0))
        shape.color = pygame.color.THECOLORS["green"]
        self.space.add(body, shape)
        shape.collision_type = 2

        goal = GameObject(body, shape)
        self.goals.append(goal)

        return goal

    def add_player_ship(self, x, y, width, height, color):
        """
        Call this after you have created the level!
        Creates a new Ship instance and adds a shape and body to the pymunk space
        :param self:
        :param x:
        :param y:
        :param width:
        :param height:
        :param color:
        :return:
        """

        ship = Ship(x, y, width, height, color)
        ship.add_lidar(self.level.shapes)

        self.space.add(ship.body, ship.shape)

        return ship

    def add_ship(self, x, y, width, height, color):
        """
        Creates a new Ship instance and adds a shape and body to the pymunk space
        :param self:
        :param x:
        :param y:
        :param width:
        :param height:
        :param color:
        :return:
        """
        ship = Ship(x, y, width, height, color)
        self.space.add(ship.body, ship.shape)

        return ship

    def get_screen(self):
        """
        Returns the game's screen space buffer as a 3D (color) array
        :return:
        """
        return pygame.surfarray.array3d(self.screen)

    def handle_discrete_action(self, action):
        """
        Handle discrete actions: It is possible to move forward, rotate left and right and do nothing.
        Moving backwards is not possible, but is easy to add if needed. See the player definition in models for this.
        :param action: integer value to indicate the action to take
        """
        if action == 0:
            self.player.move_forward()
        elif action == 1:
            self.player.rotate(-5)
        elif action == 2:
            self.player.rotate(+5)
        elif action == 3:
            pass

    def handle_input(self):
        """
        Maps key inputs to actions (via handle_discrete_action) and other utility functions such as quit
        """

         # Handle key strokes
        for event in pygame.event.get():

            # print(event.key)
            if event.type == pygame.QUIT:
                sys.exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    sys.exit(0)

                elif event.key == pygame.K_w:
                    self.handle_discrete_action(0)
                    print("W pressed. ")
                elif event.key == pygame.K_s:
                    print("S pressed. Button not configured")
                    # self.handle_discrete_action(1)
                elif event.key == pygame.K_a:
                    self.handle_discrete_action(1)
                    print("A pressed. ", self.player.rudder_angle)
                elif event.key == pygame.K_d:
                    self.handle_discrete_action(2)
                    print("D pressed. ", self.player.rudder_angle)


    def update(self):
        """
        The main update loop, resets certain event states, handles input, sensor routines and updates the game's
        pymunk space
        """
        self.colliding = False
        self.goal_reached = False
        self.handle_input()
        self.player.query_sensors()
        self.space.step(self.speed * self.base_dt)
        self.clock.tick(self.fps)

    def render(self):
        """
        The main render loop clears the screen and draws primitives if requested
        """
        self.screen.fill((0, 0, 200))
        if self.debug_mode:
            options = pm.pygame_util.DrawOptions(self.screen)
            options.flags = pymunk.SpaceDebugDrawOptions.DRAW_SHAPES
            self.space.debug_draw(options)

            res = self.player.lidar.query_results
            for r in res:
                if r is not None and r.shape is None:
                    p = r.point
                    p = self.invert_p(p)
                    p = (round(p.x), round(p.y))

                    # Green circle indicating the rays did not hot anything
                    pygame.draw.circle(self.screen, (0, 255, 0), p, 10)
                else:
                    p = r.point
                    p = self.invert_p(p)
                    p = (round(p.x), round(p.y))

                    # Red circle
                    pygame.draw.circle(self.screen, (255, 0, 0), p, 10)

        p = self.invert_p(self.player.position)

        pygame.draw.circle(self.screen, (255, 255, 0), (round(p.x), round(p.y)), 10)
        pygame.display.flip()

        self.frame_counter += 1


    def collide_ship(self, arbiter, space, data):
        """
        Ship collision callback for when the player ship hits another ship. All params are ignored at this point
        :param arbiter:
        :param space:
        :param data:
        :return:
        """
        self.colliding = True
        return True

    def collide_goal(self, arbiter, space, data):
        """
        Ship collision callback for when the player ship hits a goal object. All params are ignored at this point
        :param arbiter:
        :param space:
        :param data:
        :return:
        """
        shape = arbiter.shapes[1]
        space.remove(shape, shape.body)

        self.goal_reached = True
        self.goals = [g for g in self.goals if g.body is not shape.body]

        return False


    def reset(self):
        """
        Reset the game. Create the environment, the player and the goals
        :param spawn_point:
        :return:
        """
        self.total_goals = 0
        self.ships = list()
        self.goals = list()
        self.space = pm.Space()
        self.space.damping = 0.4
        self.create_environment()
        self.gen_goal_path(N_GOALS)

        spawn_point = Vec2d(self.bounds[0] / 2, 25)
        self.player = self.add_player_ship(spawn_point.x, spawn_point.y, 2, 3, pygame.color.THECOLORS["white"])
        self.player.shape.collision_type = 0
        self.setup_collision_handlers()

    def add_default_traffic(self):
        """
        Add some simple static traffic to the game
        :return:
        """
        self.ships.append(self.add_ship(100, 200, 1, 1, pygame.color.THECOLORS["black"]))
        self.ships.append(self.add_ship(300, 200, 1.5, 2, pygame.color.THECOLORS["black"]))
        self.ships.append(self.add_ship(400, 350, 1, 3, pygame.color.THECOLORS["black"]))

    def setup_collision_handlers(self):
        """
        Add collision handlers to the game space for goal and obstacle interactions.
        """
        h = self.space.add_collision_handler(0, 1)
        h.begin = self.collide_ship

        goal_agent_col = self.space.add_collision_handler(0, 2)
        goal_agent_col.begin = self.collide_goal

        self.space.add_collision_handler(0, 3)

    def gen_goal_path(self, n):
        """
        Generate a path of goals by sampling somewhat randomly the coordinate space. To avoid complete randomness
        where it is hard to even see a path, I kind of use a jittery approach where delta_y is computed according to
        the game bounds and incremented, and randomly jittered. The X position is determined by taking a jittered
        point close to the midline and doing a segment query to the left and right on environmental level shapes (see
        ShapeFilter). These points are then used as extreme points between which the X value is determined according
        to some tolerance value.
        :param n: number of goals to generate
        """

        y_delta = self.bounds[1] / (n+1)
        x_middle = self.bounds[0] / 2
        x_jitter = 50
        y_jitter = 20

        tolerance = 60
        filter = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS ^ 0b1) # This has not been properly tested!

        for i in range(1, n+1):
            y = y_delta*i + random.randint(-y_jitter, y_jitter)
            try:
                left_ret = self.space.segment_query((self.bounds[0]/2, y), (0, y), 10, filter)[0]
                right_ret = self.space.segment_query((self.bounds[0] / 2, y), (self.bounds[0], y), 10, filter)[0]

                x = np.random.uniform(left_ret.point.x + tolerance, right_ret.point.x - tolerance)
                self.add_goal(x, y)

            except Exception as e:
                x = x_middle * i + random.randint(-x_jitter, x_jitter)
                self.add_goal(x, y)


    def closest_goal(self):
        """
        Return the goal with the smallest Euclidean distance to the player. Returns None if there are no goals left.
        :return:
        """
        if len(self.goals):
            min_goal = self.goals[0]
            min_distance = min_goal.body.position.get_distance(self.player.body.position)
            for goal in self.goals[1:]:

                dist = goal.body.position.get_distance(self.player.body.position)
                if dist < min_distance:
                    min_distance = dist
                    min_goal = goal

            return min_goal
        return None

    def create_environment(self):
        """
        The hook for creating the environment. Replace the call for gen_level
        :return:
        """
        self.gen_level()


def main():

    import os

    cwd = os.getcwd()
    gc = GameConfig
    gc.SPEED = 1
    gc.FPS = 30
    gc.DEBUG = True

    g = ShipGame()

    while True:
        g.update()
        g.render()



if __name__ == '__main__':
    main()
