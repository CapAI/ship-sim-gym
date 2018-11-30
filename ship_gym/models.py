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
        self.max_angle = 8

    @property
    def x(self):
        return self.body.position.x

    @property
    def y(self):
        return self.body.position.y

    def move_forward(self):
        self.body.apply_force_at_local_point(self.force_vector, self.point_of_thrust)
        # self.draw_force()

    def move_backward(self):
        self.body.apply_force_at_local_point((0, -30), (0, -5))
        # self.draw_force()

    def clamp_rudder(self):
        if self.rudder_angle < -self.max_angle:
            self.rudder_angle = -self.max_angle
        elif self.rudder_angle > self.max_angle:
            self.rudder_angle = self.max_angle

    def rotate(self, angle_incr):

        self.rudder_angle += angle_incr
        self.clamp_rudder()

        self.point_of_thrust.x = self.body.center_of_gravity.x - self.rudder_angle

        # self.draw_force()