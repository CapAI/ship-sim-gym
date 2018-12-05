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
from ship_gym.models import GameObject, Ship, GeoMap, LiDAR

SHIP_TEMPLATE = [(0, 0), (0, 10), (5, 15), (10, 10), (10, 0)]

DEFAULT_BOUNDS = (500, 500)

class ShipGame():

    ships = list()
    goals = list()

    # TODO: Change this to some event enum
    colliding = False
    frame_counter = 0

    observe_mode = False
    record = False

    game_frame_dir = "_frames"

    base_dt = 0.1

    __temp_fps = 0

    def __init__(self, game_config):

        self.speed = game_config.SPEED
        self.fps = game_config.FPS
        self.bounds = game_config.BOUNDS
        self.screen = pygame.display.set_mode(self.bounds)
        self.clock = pygame.time.Clock()
        self.goal_reached = False
        self.colliding = False
        self.debug_mode = game_config.DEBUG

        os.makedirs(self.game_frame_dir, exist_ok=True)

        pygame.init()
        pygame.display.set_caption("Ship Sim Gym")
        pygame.key.set_repeat(10, 10)

        print("Init game at speed = ", self.speed)
        print("Init game at fps = ", self.fps)

        self.reset()

    def gen_level(self):

        # print("GENERATING RIVER POLY")
        poly = game_map.gen_river_poly(self.bounds)

        self.level = GeoMap(poly, self.bounds)
        # self.level = GeoMap([[[10,10],[10,20]]], self.bounds)

        for body, shape in zip(self.level.bodies, self.level.shapes):
            self.space.add(body, shape)

    def load_level(self):

        # print("Load level")
        poly = game_map.load_from_pickle("data/pickles/2R70995Alnd.pck")

        self.level = GeoMap(poly, self.bounds)

        for body, shape in zip(self.level.bodies, self.level.shapes):
            self.space.add(body, shape)


    def invert_p(self, p):
        """Because in screen Y=0 is at the top or some shit like that """
        return Vec2d(p[0], self.bounds[1] - p[1])

    def add_goal(self, x, y):
        """Add a ball to the given space at a random position"""
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
        return pygame.surfarray.array3d(self.screen)

    def handle_action(self, action):
        if action == 0:
            # print("W pressed : forwards")
            self.player.move_forward()
        # elif action == 1:
            # print("S pressed : backwards")
            # self.player.move_backward()
        elif action == 1:
            # print("A pressed : left")
            self.player.rotate(-5)
        elif action == 2:
            # print("D pressed : right")
            self.player.rotate(+5)
        elif action == 3:
            # print("Do nothing ... ")
            pass

    def handle_input(self):
        """
        Maps key inputs to actions (via handle_action)
        """

         # Handle key strokes
        for event in pygame.event.get():
            # print(event.key)
            if event.type == pygame.QUIT:
                sys.exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit(0)

                elif event.key == pygame.K_w:
                    # print("W pressed")
                    self.handle_action(0)
                elif event.key == pygame.K_s:
                    # print("S pressed")
                    self.handle_action(1)
                elif event.key == pygame.K_a:
                    # print("A pressed")
                    self.handle_action(2)
                elif event.key == pygame.K_d:
                    # print("D pressed")
                    self.handle_action(3)
                elif event.key == pygame.K_r:
                    self.observe_mode = not self.observe_mode

                    if self.observe_mode:
                        print("OBSERVE MODE ACTIVATED ... ")
                        self.__temp_fps = self.fps
                    else:
                        print("OBSERVE MODE DEACTIVATED ... ")
                        self.fps = self.__temp_fps

                elif event.key == pygame.K_t:
                    self.player.body.angle += 0.1
                    print("Test function  ... ")


                elif event.key == pygame.K_r:
                    self.record_mode = not self.record_mode


    def update(self):
        self.colliding = False
        self.goal_reached = False
        self.handle_input()

        self.player.query_sensors()

        self.space.step(self.speed * self.base_dt)
        self.clock.tick(self.fps)

    def render(self):

        self.screen.fill((0, 0, 200))


        # if self.graphics_enabled:
        #     pm.space_debug_draw_options

        if self.debug_mode:
            options = pm.pygame_util.DrawOptions(self.screen)
            options.flags = pymunk.SpaceDebugDrawOptions.DRAW_SHAPES
            self.space.debug_draw(options)
            # res = self.player.lidar.query_results
            # for r in res:
            #     # p = Vec2d(self.player.x + r.point.x, self.player.y + r.point.y)
            #     if r is not None and r.shape is None:
            #         p = r.point
            #         p = self.invert_p(p)
            #         p = (round(p.x), round(p.y))
            #
            #         # Green
            #         pygame.draw.circle(self.screen, (0, 255, 0), p, 10)
            #
            #     else:
            #         p = r.point
            #         p = self.invert_p(p)
            #         p = (round(p.x), round(p.y))
            #
            #         # Red circle
            #         pygame.draw.circle(self.screen, (255, 0, 0), p, 10)

        p = self.invert_p(self.player.position)

        # pygame.draw.circle(self.screen, (255, 255, 0), (round(p.x), round(p.y)), 10)
        pygame.draw.circle(self.screen, (255, 255, 0), (round(p.x), round(p.y)), 10)
        pygame.display.flip()

        #pygame.image.save(screen, os.path.join(game_frame_dir, f"frame_{frame_counter}.jpg"))
        self.frame_counter += 1


    def collide_ship(self, x, y, z):
        """
        Ship collision callback for when the player ship hits another NPC ship
        :param self:
        :param x:
        :param y:
        :param z:
        :return:
        """
        # print("Collide with environment!!")
        self.colliding = True
        return True

    def collide_goal(self, arbiter, space, data):
        # print(" !!! REACHED GOAL !!! ")

        brick_shape = arbiter.shapes[1]
        space.remove(brick_shape, brick_shape.body)
        self.goal_reached = True

        self.goals = [g for g in self.goals if g.body is not brick_shape.body]

        return False


    # DEFAULT_SPAWN_POINT = Vec2d(10, 20)
    def reset(self, spawn_point=None):

        if spawn_point is None:
            spawn_point = Vec2d(self.bounds[0] / 2, 25)
        if not isinstance(spawn_point, Vec2d):
            spawn_point = Vec2d(spawn_point)

        self.total_goals = 0
        self.ships = list()
        self.goals = list()
        self.space = pm.Space()
        self.space.damping = 0.4

        # print("CREATING ENVIRONMENT .... ")
        self.create_environment()
        self.gen_goal_path(5, Vec2d(self.bounds[0] / 2, 50))
        self.player = self.add_player_ship(spawn_point.x, spawn_point.y, 2, 3, pygame.color.THECOLORS["white"])

        self.player.shape.collision_type = 0
        self.setup_collision_handlers()

    def add_default_traffic(self):
        self.ships.append(self.add_ship(100, 200, 1, 1, pygame.color.THECOLORS["black"]))
        self.ships.append(self.add_ship(300, 200, 1.5, 2, pygame.color.THECOLORS["black"]))
        self.ships.append(self.add_ship(400, 350, 1, 3, pygame.color.THECOLORS["black"]))

    def setup_collision_handlers(self):
        h = self.space.add_collision_handler(0, 1)
        h.begin = self.collide_ship

        goal_agent_col = self.space.add_collision_handler(0, 2)
        goal_agent_col.begin = self.collide_goal

        self.space.add_collision_handler(0, 3)

    def gen_goal_path(self, n, start_pos):

        """
        NOTE: This is wildly inefficient but at least it's general!
        :param n:
        :param start_pos:
        :return:
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

                # print(left_ret.point)
                # print(right_ret.point)

                x = np.random.uniform(left_ret.point.x + tolerance, right_ret.point.x - tolerance)
                self.add_goal(x, y)

            except Exception as e:
                # print("WOOPS", e)
                x = x_middle * i + random.randint(-x_jitter, x_jitter)
                self.add_goal(x, y)


    def closest_goal(self):
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
        self.gen_level()


def main():

    import os

    cwd = os.getcwd()
    # print(cwd)
    g = ShipGame(debug_mode=True)

    while True:

        g.update()
        g.render()

        # print(f"My position = \t{player.x},{player.y}")


if __name__ == '__main__':
    main()
