from pygame.math import Vector2

class PlayerShip(object):

    def __init__(self, x, y):

        self.velocity = Vector2(0, 0)
        self.heading = Vector2(0, 0)
        self.pos = Vector2(x, y)

    def update(self, t_delta):

        self.pos = 

    def accelerate(self, )