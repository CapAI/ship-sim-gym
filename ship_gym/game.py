import os
import random
import sys

import numpy as np
import pygame

from pymunk import Vec2d, Transform
import pymunk as pm
import pymunk.pygame_util

from ship_gym import game_map
from ship_gym.models import GameObject, Ship, GeoMap

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

    def __init__(self, speed=1, fps=30, bounds=DEFAULT_BOUNDS):

        self.speed = speed
        self.fps = fps
        self.bounds = bounds
        self.screen = pygame.display.set_mode(bounds)
        self.clock = pygame.time.Clock()
        self.goal_reached = False
        self.colliding = False

        os.makedirs(self.game_frame_dir, exist_ok=True)

        pygame.init()
        pygame.display.set_caption("Ship Sim Gym")
        pygame.key.set_repeat(10, 10)

        print("Init game at speed = ", speed)
        print("Init game at fps = ", fps)

        self.reset()
        self.load_level()

    def load_level(self):

        print("Load level")
        # poly = game_map.load_from_pickle("data/pickles/2R70995Alnd.pck")

        poly = game_map.gen_river_poly(self.bounds)
        self.level = GeoMap(poly, self.bounds)

        # Add all the shapes to the space
        # print(self.level.bb())
        bb = self.level.bb()
        print(bb)

        # Realign map to bounds
        print(bb.left, bb.top)

        scale_x = self.bounds[0] / (bb.right - bb.left)
        scale_y = self.bounds[1] / (bb.top - bb.bottom)

        self.level.transform(Transform(a=scale_x, d=scale_y, tx=-bb.left, ty=-bb.bottom))

        for body, shape in zip(self.level.bodies, self.level.shapes):

            print("Add level body, shape : ", body, shape)

            # mass = 2
            # points = [(x[0] * 1, x[1] * 1) for x in SHIP_TEMPLATE]
            # moment = pm.moment_for_poly(mass, points)
            #
            # # moment = 1000
            # body = pm.Body(mass, moment)
            # body.position = Vec2d(300, 300)
            # shape = pm.Poly(body, points)
            # shape.friction = 0.5

            # c_i = random.choice(pygame.color.THECOLORS)

            # shape.collision_type = 1

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
        # ship.body.angle = 1.57079633 # + 90 degrees
        self.space.add(ship.body, ship.shape)

        return ship

    def get_screen(self):
        return pygame.surfarray.array3d(self.screen)

    def handle_action(self, action):
        if action == 0:
            # print("W pressed : forwards")
            self.player.move_forward()
        elif action == 1:
            # print("S pressed : backwards")
            self.player.move_backward()
        elif action == 2:
            # print("A pressed : left")
            self.player.rotate(-10)
        elif action == 3:
            # print("D pressed : right")
            self.player.rotate(+10)
        elif action == 4:
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
                    print("Test function  ... ")


                elif event.key == pygame.K_r:
                    self.record_mode = not self.record_mode


    def update(self):
        self.colliding = False
        self.goal_reached = False

        # self.

        self.handle_input()
        self.space.step(self.speed * self.base_dt)
        self.clock.tick(self.fps)

    def render(self):

        self.screen.fill((0, 0, 200))

        draw_options = pm.pygame_util.DrawOptions(self.screen)
        self.space.debug_draw(draw_options)

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
        self.colliding = True
        return True

    def collide_goal(self, arbiter, space, data):
        # print(" !!! REACHED GOAL !!! ")

        brick_shape = arbiter.shapes[1]
        space.remove(brick_shape, brick_shape.body)
        self.goal_reached = True

        self.goals = [g for g in self.goals if g.body is not brick_shape.body]

        return False


    DEFAULT_SPAWN_POINT = Vec2d(10, 20)
    def reset(self, spawn_point=DEFAULT_SPAWN_POINT):

        if not isinstance(spawn_point, Vec2d):
            spawn_point = Vec2d(spawn_point)

        self.total_goals = 0
        self.ships = list()
        self.goals = list()

        self.space = pm.Space()
        self.space.damping = 0.4

        self.player = self.add_ship(spawn_point.x, spawn_point.y, 2, 3, pygame.color.THECOLORS["white"])
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

    def closest_goal(self):
        if len(self.goals):
            min_goal = self.goals[0]
            min_distance = min_goal.body.position.get_distance(self.player.body.position)
            for goal in self.goals[1:]:

                dist = goal.body.position.get_distance(self.player.body.position)
                if dist < min_distance:
                    min_distance = dist
                    min_goal = goal

            # print("Min goal = ", min_goal)
            return min_goal
        return None



def main():

    import os
    cwd = os.getcwd()
    print(cwd)

    g = ShipGame()

    while True:

        g.update()
        g.render()

        # print(f"My position = \t{player.x},{player.y}")


if __name__ == '__main__':
    main()
