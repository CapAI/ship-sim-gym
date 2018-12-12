# From dashboard/visualizer:
import json
import pickle
import random

def load_from_pickle(path):
    """
    Load a polygon set from pickle, the assumed format here is a 2D list where each list contains lists of either X or Y
    values of the polygon shape.
    :param path:
    :return:
    """
    poly_list = pickle.load(open(path, "rb"))

    # Unwrap the poly list
    vertex_group = list()
    for lats, longs in zip(poly_list[0], poly_list[1]):
        vertex_group.append(list(zip(lats, longs)))

    return vertex_group

def gen_river_poly(bounds, N=10, width_frac=0.5):
    """
    Not the prettiest of code, but this will generate two segments of vertically aligned river banks or shore polygons.
    You can use these polygons to create shapes and bodies from for physics computation. It is highly recommended you
    turn them into STATIC type bodies so the physics computation cost is much lower.

    Please note that there are still quite a few
    :param bounds: The bounds in which to operate.
    :param N:
    :return:
    """

    y_start = -100
    y_delta = (bounds[1]*1.2-y_start) / N

    bank_width = width_frac * bounds[0] / 2

    def river_bank_helper(n_segments, x_min, x_max, y_jitter=20, x_jitter=50, max_tries=1000):
        """
        Kind of brute force approach to trying to generate a single shore polygon.
        :param n_segments:
        :param x_min:
        :param x_max:
        :return:
        """
        vs = list()
        x_middle = x_min + (x_max - x_min)

        for i in range(1, n_segments+1):

            invalid_pos = True
            try_i = 0
            while invalid_pos:
                x = random.gauss(x_middle, x_jitter)
                y = y_start + random.gauss(y_delta * i, y_jitter)
                invalid_pos = x < x_min or x > x_max
                try_i += 1

                if try_i >= max_tries:
                    break

            vs.append([x, y])

        return vs

    left_vs = river_bank_helper(N, 0, bank_width)
    left_vs.extend([[0, bounds[1]], [0, 0]])

    right_vs = river_bank_helper(N, bounds[0] - bank_width, bounds[0])
    right_vs.extend([[bounds[0], bounds[1]], [bounds[0], 0]])

    return [left_vs, right_vs]