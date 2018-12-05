import math
import random

import pygame
from pygame.rect import Rect

from pymunk import Vec2d, Body, Transform, BB

SHIP_TEMPLATE = [(0, 0), (0, 10), (5, 15), (10, 10), (10, 0)]

import pymunk as pm

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

        :param shapes:
        :return:
        """

        angle_delta = math.radians(self.spread / self.n_beams)
        angle_start = self.ship.body.angle + math.radians(90 - self.spread / 2)

        # print("self.angle = ", math.degrees(self.ship.body.angle))
        # print("angle start = ", angle_start)

        bb = self.ship.shape.bb
        cx = self.ship.x + (bb.right - bb.left) / 2
        cy = self.ship.y + (bb.top - bb.bottom) / 2
        origin = Vec2d(cx, cy)

        # print("----------------------------------------")
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
                    # print(distance)
                    self.vals[i] = distance
                    break

            self.query_results.append(query_result)

        # print(f"LIDAR QUERY FOUND {len(self.query_results)} RESULTS ... ")
        return self.query_results

    def values(self):
        """

        :return:
        """
        for q in self.query_results:
            if q.shape is not None:
                return


class Ship(object):

    def __init__(self, x, y, width, height, color, mass=5, lidar=None):
        """

        :param x:
        :param y:
        :param width:
        :param height:
        :param color:
        :param mass:
        """

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
        # shape.transform =
        self.filter = pm.ShapeFilter(categories=0b1)
        self.width = width
        self.height = height
        self.shape = shape
        self.body = body
        self.force_vector = Vec2d(0, 100)
        self.rudder_angle = 0
        # self.point_of_thrust = self.body.center_of_gravity
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

    def add_lidar(self, track_shapes):
        self.lidar = LiDAR(self, track_shapes)


class GeoMap(object):

    bodies = None
    shapes = None

    def __init__(self, poly_list, bounds):
        self.poly_list = poly_list
        self.bounds = bounds

        if poly_list is not None:
            self.gen_bodies(poly_list) #IMPORTANT TO DO FIRST!!
            self.gen_shapes(poly_list)
        # self.gen_shapes_reorient(poly_list)



    def transform(self, tf):

        print("Transform map", tf)
        for shape in self.shapes:
            # shape.update(tf)
            shape.transform = tf
            print(shape.get_vertices())

        print("New bounding box : ", self.bb())
        print("")

    def gen_shapes(self, vertex_group):
        self.shapes = list()
        for vs, body in zip(vertex_group, self.bodies):

            shape = pm.Poly(body, vs)
            shape.color = (139, 69, 19)
            shape.collision_type = 1

            self.shapes.append(shape)

    def gen_shapes_reorient(self, vertex_group):
        """
        Generate shapes
        :param vertex_group:
        :return:
        """

        self.shapes = list()

        # Find bounds and
        min_x = 10000000
        min_y = 10000000
        max_x = -10000000
        max_y = -10000000
        for vertices in vertex_group:

            for v in vertices:
                min_x = min(v[0], min_x)
                min_y = min(v[1], min_y)
                max_x = max(v[0], max_x)
                max_y = max(v[1], max_y)

        print(min_x, min_y, max_x, max_y)

        self.geo_bounds = BB(min_x, min_y, max_x, max_y)

        tx = -self.geo_bounds.left
        ty = -self.geo_bounds.bottom

        sx = self.bounds[0] / (self.geo_bounds.right - self.geo_bounds.left)
        sy = self.bounds[1] / (self.geo_bounds.top - self.geo_bounds.bottom)

        print("sx = ", sx)
        print("sy = ", sy)
        print("tx = ", tx)
        print("ty = ", ty)

        for vertices, body in zip(vertex_group, self.bodies):

            # mass = 2
            # vertices = [(x[0] * 100, x[1] * 200) for x in SHIP_TEMPLATE]

            # vertices = [(int(x[0]) * 10, int(x[1]) * 20) for x in vertices]
            # print(vertices)
            # moment = pm.moment_for_poly(mass, points)

            # moment = 1000
            # body = pm.Body(mass, moment)
            # body.position = Vec2d(x, y)
            # shape.friction = 0.5
            # shape.color = color

            # shape = pm.Poly(body, vertices)
            # shape.collision_type = 1

            # print()
            # vs = [v * ]
            # transform = Transform(tx=tx, ty=ty)
            # transform = Transform(a=sx, d=sy)
            # print(transform)

            vs = [((x + tx) * sx,(y + ty) * sy) for (x,y) in vertices]
            print("-----")
            print(len(vertices))
            print(vertices)
            print(vs)
            print("-----")
            shape = pm.Poly(body, vs)

            def random_color():
                rgbl = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
                random.shuffle(rgbl)
                return tuple(rgbl)

            print(shape.get_vertices())
            # shape.color = pygame.color.THECOLORS["red"]
            shape.color = random_color()
            shape.collision_type = 1

            # print("NEW SHAPE = ", shape.update(Transform(10, 0, 0, 10, 0, 0)))
            if len(vertices) > 100:
                print(vertices)
                self.shapes.append(shape)
                # break


            # break

        # for shape in self.shapes:
            # shape.transform = Transform(a=10, d=10)
            # shape.update(Transform(a=10, d=10))

            # print(shape.get_vertices())



    def gen_bodies(self, vertex_group, mass=1):

        self.bodies = list()
        for vertices in vertex_group:
            # moment = pm.moment_for_poly(mass, vertices)

            # mass = 2
            # points = [(x[0] * 1, x[1] * 1) for x in SHIP_TEMPLATE]
            # moment = pm.moment_for_poly(mass, points)
            #
            # # moment = 1000
            # body = pm.Body(mass, moment)
            # body.position = Vec2d(100, 100)

            body = pm.Body(None, None, body_type=Body.STATIC)
            # body.position = (100, 100)

            self.bodies.append(body)

            # body.position = Vec2d(x, y)

    def bb(self):
        # min_x, min_y = 10000000, 10000000
        # max_x, max_y = -10000000, -1000000

        total_bb = self.shapes[0].update(Transform.identity())
        for s in self.shapes[1:]:
            bb = s.update(Transform.identity())
            print("part bb = ", bb)
            total_bb.merge(bb)

        return total_bb


