import os
import sys
import pygame

from pymunk import Vec2d
import pymunk as pm
import pymunk.pygame_util

space = None
bounds = (500, 500)

SHIP_TEMPLATE = [(0,0), (0,10), (5,15), (10,10), (10,0)]
screen = None
clock = None
player = None

ships = list()
goals = list()

#TODO: Change this to some event enum
colliding = False
goal_reached = False
frame_counter = 0

game_frame_dir = "/Users/gerard/Desktop/frames"
os.makedirs(game_frame_dir, exist_ok=True)

base_dt = 0.1

def invert_p(p):
    ''' Because in screen Y=0 is at the top or some shit like that '''
    return Vec2d(p[0], bounds[1] - p[1])


class GameObject(object):

    def __init__(self, body, shape):
        self.body = body
        self.shape = shape



class Ship(object):

    def __init__(self, x, y, width, height, color):

        mass = 2
        points = [(x[0] * width, x[1] * height) for x in SHIP_TEMPLATE]
        moment = pm.moment_for_poly(mass, points) 

        #moment = 1000
        body = pm.Body(mass, moment)
        body.position = Vec2d(x,y)       
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
        p1 = self.body.local_to_world(self.point_of_thrust)
        p2 = self.body.local_to_world(self.point_of_thrust - self.force_vector)

        p1 = invert_p(p1)
        p2 = invert_p(p2)

        pygame.draw.line(screen, (0, 255, 0), p1, p2)

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



def add_goal(x, y):
    """Add a ball to the given space at a random position"""
    mass = 1
    radius = 5
    inertia = pm.moment_for_circle(mass, 0, radius, (0,0))
    body = pm.Body(mass, inertia)
    
    body.position = x, y
    shape = pm.Circle(body, radius, (0,0))
    shape.color = pygame.color.THECOLORS["green"]
    space.add(body, shape)
    shape.collision_type = 2

    return GameObject(body, shape)

def add_ship(x, y, width, height, color):
    ship = Ship(x, y, width, height, color)
    space.add(ship.body, ship.shape)

    return ship

def get_screen():
    return pygame.surfarray.array3d(screen)

def handle_action(action):
    if action == 0:
        # print("W pressed : forwards")
        player.move_forward()
    elif action == 1:
        # print("S pressed : backwards")
        player.move_backward()
    elif action == 2:
        # print("A pressed : left")
        player.rotate(-10)
    elif action == 3:
        # print("D pressed : right")
        player.rotate(+10)
    elif action == 4:
        # print("Do nothing ... ")
        pass

def handle_input():
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
                handle_action(0)
            elif event.key == pygame.K_s:
                # print("S pressed")
                handle_action(1)
            elif event.key == pygame.K_a:
                # print("A pressed")
                handle_action(2)
            elif event.key == pygame.K_d:
                # print("D pressed")
                handle_action(3)
            elif event.key == pygame.K_r:
                reset()


def update():
    global goal_reached, colliding

    goal_reached = False
    colliding = False

    handle_input()

    space.step(speed * base_dt)

    clock.tick(fps)

def render():
    global frame_counter
    # print(" GAME RENDER !!!!")

    screen.fill((0, 0, 200))

    draw_options = pm.pygame_util.DrawOptions(screen)
    space.debug_draw(draw_options)

    pygame.display.flip()

    pygame.image.save(screen, os.path.join(game_frame_dir, f"frame_{frame_counter}.jpg"))
    frame_counter += 1
    

def collide_ship(x, y, z):
    # print("COLLIDE WITH SHIP")
    global colliding
    colliding = True

    return True

def collide_goal(arbiter, space, data):

    # print("REACHED GOAL")

    brick_shape = arbiter.shapes[1] 
    space.remove(brick_shape, brick_shape.body)
    global goal_reached
    goal_reached = True

    return False

def init(_speed=1, _fps=30):
    global space, player, screen, clock, speed, fps


    speed = _speed
    fps = _fps

    print("Init game at speed = ", speed)
    print("Init game at fps = ", fps)
    pygame.init()
    
    screen = pygame.display.set_mode(bounds)
    pygame.display.set_caption("Ship Sim Gym")
    pygame.key.set_repeat(10, 10)
    clock = pygame.time.Clock()
    
def reset():

    global space, player, screen, clock, goals

    ships = list()
    goals = list()

    if space is not None:
        del space
    space = pm.Space()

    player = add_ship(300, 100, 2, 3, pygame.color.THECOLORS["white"])
    player.shape.collision_type = 0
    # print("Player added at ", player.body.position)

    ships.append(add_ship(100, 200, 1, 1, pygame.color.THECOLORS["black"]))
    ships.append(add_ship(300, 200, 1.5, 2, pygame.color.THECOLORS["black"]))
    ships.append(add_ship(400, 350, 1, 3, pygame.color.THECOLORS["black"]))

    goals.append(add_goal(300,150))
    goals.append(add_goal(200,200))
    goals.append(add_goal(300,500))
    
    space.damping = 0.4

    h = space.add_collision_handler(0, 1)
    h.begin = collide_ship

    goal_agent_col = space.add_collision_handler(0, 2)
    goal_agent_col.begin = collide_goal

def closest_goal():


    if len(goals):
        min_goal = goals[0]
        min_distance = min_goal.body.position.get_distance(player.body.position)
        for goal in goals[1:]:

            dist = goal.body.position.get_distance(player.body.position)
            if dist < min_distance:
                min_distance = dist
                min_goal = goal

        return min_goal
    return None



def main():

    init()
    reset()

    while True:

        update()
        render()

        # print(f"My position = \t{player.x},{player.y}")


if __name__ == '__main__':
    main()