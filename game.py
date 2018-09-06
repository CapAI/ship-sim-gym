import sys, random
import pygame

from pygame import Color
from pygame.locals import *

from pymunk import Vec2d
import pymunk as pm
import pymunk.pygame_util

space = None
bounds = (600, 600)

SHIP_TEMPLATE = [(0,0), (0,10), (5,15), (10,10), (10,0)]
screen = None

class Ship(object):

    def __init__(self, shape, body):

        self.shape = shape
        self.body = body
        self.force_vector = (0, 1)

    def move_forward(self):
        self.body.apply_force_at_local_point((0, 100), (0, -5))

        print(dir(self.body))
        p1 = self.body.local_to_world((0, -5))
        p2 = self.body.local_to_world((0, 100))
        p1 = [int(x) for x in p1]
        p2 = [int(x) for x in p2]
        print(p1)
        print(p2)
        pygame.draw.line(screen, Color("green"), p1, p2)

    def move_backward(self):
        self.body.apply_force_at_local_point((0, -30), (0, -5))

    def move_left(self):
        self.body.apply_force_at_local_point((30, 0), (0, -5))

    def move_right(self):
        self.body.apply_force_at_local_point((-30, 0), (0, -5))




def add_ball():
    """Add a ball to the given space at a random position"""
    mass = 1
    radius = 14
    inertia = pm.moment_for_circle(mass, 0, radius, (0,0))
    body = pm.Body(mass, inertia)
    x = random.randint(120,380)
    body.position = x, 550
    shape = pm.Circle(body, radius, (0,0))
    space.add(body, shape)

    body.apply_force_at_local_point((100, 50), (0, 5))

    return shape

# def create_ship(x, y, scale):
    # """  """



def add_ship(x, y, width, height):

    mass = 2
    points = [(x[0] * width, x[1] * height) for x in SHIP_TEMPLATE]
    moment = pm.moment_for_poly(mass, points)    
    #moment = 1000
    body = pm.Body(mass, moment)
    body.position = Vec2d(x,y)       
    shape = pm.Poly(body, points)
    shape.friction = 0.5
    shape.collision_type = 0
    space.add(body, shape)

    return Ship(shape, body)



def add_L(space):
    """Add a inverted L shape with two joints"""
    rotation_center_body = pm.Body(body_type = pm.Body.STATIC)
    rotation_center_body.position = (300,300)

    rotation_limit_body = pm.Body(body_type = pm.Body.STATIC)
    rotation_limit_body.position = (200,300)

    body = pm.Body(10, 10000)
    body.position = (300,300)

    l1 = pm.Segment(body, (-150, 0), (255.0, 0.0), 5.0)
    l2 = pm.Segment(body, (-150.0, 0), (-150.0, 50.0), 5.0)

    rotation_center_joint = pm.PinJoint(body, rotation_center_body, (0,0), (0,0))
    joint_limit = 25
    rotation_limit_joint = pm.SlideJoint(body, rotation_limit_body, (-100,0), (0,0), 0, joint_limit)

    space.add(l1, l2, body, rotation_center_joint, rotation_limit_joint)
    return l1,l2

def handle_input():
     # Handle key strokes
    for event in pygame.event.get():
        # print(event.key)
        if event.type == QUIT:
            sys.exit(0)

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                sys.exit(0)

            elif event.key == K_w:
                print("W pressed")
                agent.move_forward()
            elif event.key == K_s:
                print("S pressed")
                agent.move_backward()
            elif event.key == K_a:
                print("A pressed")
                agent.move_left()
            elif event.key == K_d:
                print("D pressed")
                agent.move_right()

def main():
    global space, agent, screen

    pygame.init()
    screen = pygame.display.set_mode(bounds)
    pygame.display.set_caption("Ship Sim Gym")
    pygame.key.set_repeat(100,100)
    clock = pygame.time.Clock()
    
    space = pm.Space()
    space.damping = 0.3

    # space.gravity = (0.0, -900.0)
    agent = add_ship(100, 100, 2, 3)

    add_ship(100, 200, 1, 1)
    add_ship(300, 200, 1.5, 2)
    add_ship(400, 350, 1, 3)

    balls = []
    draw_options = pm.pygame_util.DrawOptions(screen)

    ticks_to_next_ball = 10
    while True:
        screen.fill((0, 0, 255))

        handle_input()

        space.debug_draw(draw_options)

        space.step(1 / 50.0)

        pygame.display.flip()
        clock.tick(50)

if __name__ == '__main__':
    main()