import os
import sys

import numpy as np
import pygame

from pymunk import Vec2d
import pymunk as pm
import pymunk.pygame_util

SHIP_TEMPLATE = [(0, 0), (0, 10), (5, 15), (10, 10), (10, 0)]


class GameObject(object):

    def __init__(self, body, shape):
        self.body = body
        self.shape = shape

    def __repr__(self):
        return f"Goal({self.x}, {self.y})"

    @property
    def x(self):
        return self.body.position.x

    @property
    def y(self):
        return self.body.position.y

class Ship(object):

    def __init__(self, x, y, width, height, color):

        mass = 2
        points = [(x[0] * width, x[1] * height) for x in SHIP_TEMPLATE]
        moment = pm.moment_for_poly(mass, points) 

        #moment = 1000
        body = pm.Body(mass, moment)
        body.position = Vec2d(x, y)
        shape = pm.Poly(body, points)
        shape.friction = 0.5
        shape.color = color   
        shape.collision_type = 1

        self.width = width
        self.height = height
        self.shape = shape
        self.body = body
        self.force_vector = Vec2d(0, 100)
        self.rudder_angle = 0

        self.point_of_thrust = self.body.center_of_gravity
        self.max_angle = 5

    @property
    def x(self):
        return self.body.position.x

    @property
    def y(self):
        return self.body.position.y

    def move_forward(self):
        self.body.apply_force_at_local_point(self.force_vector, self.point_of_thrust)
        self.draw_force()
        

    def draw_force(self):
        pass

        ''' CONTENT REMOVED, IT REQUIRED ACCESS TO GAME BOUNDS, IMPOSSIBLE NOW SINCE ITS A CLASS '''

        # p1 = self.body.local_to_world(self.point_of_thrust)
        # p2 = self.body.local_to_world(self.point_of_thrust - self.force_vector)
        #
        # # p1 = self.invert_p(p1)
        # # p2 = invert_p(p2)
        #
        # # pygame.draw.line(screen, (0, 255, 0), p1, p2)

    def move_backward(self):
        self.body.apply_force_at_local_point((0, -30), (0, -5))
        self.draw_force()

    def clamp_rudder(self):
        if self.rudder_angle < -self.max_angle:
            self.rudder_angle = -self.max_angle
        elif self.rudder_angle > self.max_angle:
            self.rudder_angle = self.max_angle

    def rotate(self, angle_incr):

        self.rudder_angle += angle_incr
        self.clamp_rudder()

        self.point_of_thrust.x = self.body.center_of_gravity.x - self.rudder_angle

        self.draw_force()


DEFAULT_BOUNDS = (500, 500)

class ShipGame():

    ships = list()
    goals = list()

    # TODO: Change this to some event enum
    colliding = False
    frame_counter = 0

    # game_frame_dir = "/Users/gerard/Desktop/frames"
    # os.makedirs(game_frame_dir, exist_ok=True)

    base_dt = 0.1

    def __init__(self, speed=1, fps=30, bounds=DEFAULT_BOUNDS):

        self.speed = speed
        self.fps = fps
        self.bounds = bounds
        self.screen = pygame.display.set_mode(bounds)
        self.clock = pygame.time.Clock()
        self.goal_reached = False
        self.colliding = False

        pygame.init()
        pygame.display.set_caption("Ship Sim Gym")
        # pygame.key.set_repeat(10, 10)

        print("Init game at speed = ", speed)
        print("Init game at fps = ", fps)

        self.reset()

    def invert_p(self, p):
        ''' Because in screen Y=0 is at the top or some shit like that '''
        return Vec2d(p[0], self.bounds[1] - p[1])

    def add_goal(self, x, y):
        """Add a ball to the given space at a random position"""
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

        print("Created goal at ", x, " ", y)
        print(f"There are now {len(self.goals)} goals in the game!")

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
                    self.reset()


    def update(self):
        self.colliding = False
        self.goal_reached = False

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
        print(" !!! REACHED GOAL !!! ")

        brick_shape = arbiter.shapes[1]
        space.remove(brick_shape, brick_shape.body)
        self.goal_reached = True

        self.goals = [g for g in self.goals if g.body is not brick_shape.body]

        return False

    def create_goals(self):

        N = 10
        for i in range(N):
            x = np.random.randint(30, self.bounds[0] - 30)
            y = np.random.randint(30, self.bounds[1] - 30)
            self.goals.append(self.add_goal(x, y))
            self.goals.append(self.add_goal(self.player.x, self.player.y + 40))

    DEFAULT_SPAWN_POINT = Vec2d(10, 20)
    def reset(self, spawn_point=DEFAULT_SPAWN_POINT):

        if not isinstance(spawn_point, Vec2d):
            spawn_point = Vec2d(spawn_point)

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

            print("Min goal = ", min_goal)
            return min_goal
        return None



def main():

    g = ShipGame()
    g.reset()

    while True:

        g.update()
        g.render()

        # print(f"My position = \t{player.x},{player.y}")


if __name__ == '__main__':
    main()
