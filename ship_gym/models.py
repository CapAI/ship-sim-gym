import math

import pymunk as pm
from pymunk import Vec2d, Body, Transform

SHIP_TEMPLATE = [(0, 0), (0, 10), (5, 15), (10, 10), (10, 0)]


class GameObject(object):
    """ Super basic GameObject wraps a body, shape and positional properties """
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


class LiDAR(object):

    def __init__(self, ship, shapes, n_beams=10, spread=90, distance=100):
        self.n_beams = n_beams
        self.spread = spread
        self.distance = distance
        self.shapes = shapes
        self.ship = ship

        self.vals = [-1] * n_beams
        self.query_results = list()

    def query(self):
        """
        Query the lidar sensor by doing segment queries in a fanned out pattern from the lidar's origin to simulate
        rays. When a segment query returns something the distance is measured to the origin and put in the lidar val
        array
        :param shapes:
        :return:
        """

        angle_delta = math.radians(self.spread / self.n_beams)
        angle_start = self.ship.body.angle + math.radians(90 - self.spread / 2)

        bb = self.ship.shape.bb
        cx = self.ship.x + (bb.right - bb.left) / 2
        cy = self.ship.y + (bb.top - bb.bottom) / 2
        origin = Vec2d(cx, cy)

        self.query_results = list()
        self.readings = [-1] * self.n_beams
        for i in range(self.n_beams):

            query_result = None
            for shape in self.shapes:
                rotation = angle_start + (angle_delta * i)
                x_end = cx + self.distance * math.cos(rotation)
                y_end = cy + self.distance * math.sin(rotation)
                dest = Vec2d(x_end, y_end)

                query_result = shape.segment_query(origin, dest)
                if query_result.shape is not None:

                    distance = query_result.point.get_distance(origin)
                    self.vals[i] = distance
                    break

            self.query_results.append(query_result)

        return self.query_results


class Ship(object):
    """
    Models a very simple ship by creating a polygon based on a rectangle for the hull and a triangle for the bow.
        See @SHIP_TEMPLATE for this. A pymunk body and shape is then created from this with some friction and mass.
        Propulsion is simulated by applying a single force vector to a given point. It is possible to manipulate the
        position of this thrust vector thereby simulating rotational movements of the vessel.
    """

    def __init__(self, x, y, width, height, color, mass=5, lidar=None):
        points = [(x[0] * width, x[1] * height) for x in SHIP_TEMPLATE]
        moment = pm.moment_for_poly(mass, points) 

        # Body creation
        body = pm.Body(mass, moment)
        body.position = Vec2d(x, y)

        # Shape creation
        shape = pm.Poly(body, points)

        shape.friction = 0.7
        shape.color = color   
        shape.collision_type = 1

        self.filter = pm.ShapeFilter(categories=0b1) # This is used for better segment querying
        self.width = width
        self.height = height
        self.shape = shape
        self.body = body
        self.force_vector = Vec2d(0, 100)
        self.rudder_angle = 0
        self.point_of_thrust = self.shape.bb.center()
        self.max_angle = 10
        self.lidar = lidar

    @property
    def position(self):
        return self.body.position

    @property
    def x(self):
        return self.body.position.x

    @property
    def y(self):
        return self.body.position.y

    def query_sensors(self):
        if self.lidar:
            self.lidar.query()

    def move_forward(self, force=1):
        self.body.apply_force_at_local_point(self.force_vector * force, self.point_of_thrust)

    def move_backward(self, force=1):
        self.body.apply_force_at_local_point(self.force_vector * -force, (0, -5))
        # self.draw_force()

    def clamp_rudder(self):
        if self.rudder_angle < -self.max_angle:
            self.rudder_angle = -self.max_angle
        elif self.rudder_angle > self.max_angle:
            self.rudder_angle = self.max_angle

    def rotate(self, angle_incr):
        print("Rotate player with ", angle_incr)
        self.rudder_angle += angle_incr
        self.clamp_rudder()
        self.point_of_thrust.x = self.body.center_of_gravity.x - self.rudder_angle


    def add_lidar(self, track_shapes):
        self.lidar = LiDAR(self, track_shapes)


class PolyEnv(object):

    bodies = None
    shapes = None

    def __init__(self, poly_list, bounds):
        """

        :param poly_list:
        :param bounds:
        """
        self.poly_list = poly_list
        self.bounds = bounds

        if poly_list is not None:
            self.gen_bodies(poly_list) #IMPORTANT TO DO FIRST!!
            self.gen_shapes(poly_list)

    def gen_shapes(self, vertex_group):
        """
        Create shapes from the vertex groups we have.
        :param vertex_group:
        :return:
        """
        self.shapes = list()
        for vs, body in zip(vertex_group, self.bodies):

            shape = pm.Poly(body, vs)
            shape.color = (139, 69, 19)
            shape.collision_type = 1

            self.shapes.append(shape)

    def gen_bodies(self, vertex_group):
        """
        Generate the body for this environment, which in it's current setting is very simple by using a static body,
        which is why we only need a single one. If you want to use dynamic bodies you would have to generate one for
        every shape.
        """
        # TODO: FIXME: A list is no longer necessary for this class, but might be useful for other similar classes where you don't use a single static body
        self.bodies = list()
        for _ in vertex_group:
            body = pm.Body(None, None, body_type=Body.STATIC)
            self.bodies.append(body)

    def bb(self):

        total_bb = self.shapes[0].update(Transform.identity())
        for s in self.shapes[1:]:
            bb = s.update(Transform.identity())
            total_bb.merge(bb)

        return total_bb


