# From dashboard/visualizer:
import json
import pickle
import random

from ship_gym.models import GeoMap


def dump_S57(ecnfilename, bokeh_land=None, bokeh_sea=None, rasterio_land=None):
    """
    WARNING: input arrays will be modified
    Use GDAL to load S57 into its required bokeh land and sea compoents.
    A properly formatted rasterio array is also returned (this is used to prepare
    raster images for the visualization and AI).

        @param (string) filename : the name of the s57 file (no path needed)
        @param (string) bokeh_land : list of lists (x - > all x points of the land polygons)
                                                    (y - > all y points of the land polygons)
        @param (string) bokeh_sea : same as above but for the sea
        @param (string) rasterio_land : list of [x,y] coordinates which is the format
                                        that rasterio requires
        @return
    """

    try:
        from osgeo import osr, ogr, gdal
    except ImportError:
        import osr, ogr

    if bokeh_land is None and bokeh_sea is None and rasterio_land is None:
        raise ValueError("You need to give at least one of bokeh_land, bokeh_sea or rasterio_land a value")

    ds = ogr.Open(ecnfilename)
    assert ds is not None, ("Could not retrieve a GDAL file handle for " + ecnfilename)

    if bokeh_land is not None or rasterio_land is not None:

        layer_block = ds.GetLayerByName('LNDARE')
        assert layer_block is not None, ("Could not retrieve Land Areas from " + ecnfilename)
        for feature in layer_block:
            feature_json_str = feature.ExportToJson()
            feature_json = json.loads(feature_json_str)
            coord_list = feature_json["geometry"]["coordinates"][0]

            if rasterio_land is not None:
                rasterio_land.append([[coord[0], coord[1]] for coord in coord_list])

            if bokeh_land is not None:
                bokeh_land[0].append([coord[0] for coord in coord_list])
                bokeh_land[1].append([coord[1] for coord in coord_list])

    if bokeh_sea:
        layer_block = ds.GetLayerByName('SEAARE')
        assert layer_block is not None, ("Could not retrieve Sea Areas from " + ecnfilename)
        for feature in layer_block:
            feature_json_str = feature.ExportToJson()
            feature_json = json.loads(feature_json_str)
            coord_list = feature_json["geometry"]["coordinates"][0]
            bokeh_sea[0].append([coord[0] for coord in coord_list])
            bokeh_sea[1].append([coord[1] for coord in coord_list])

        layer_block = ds.GetLayerByName('hrbbsn')
        assert layer_block is not None, ("Could not retrive Harbour Basins from " + ecnfilename)
        for feature in layer_block:
            feature_json_str = feature.ExportToJson()
            feature_json = json.loads(feature_json_str)
            coord_list = feature_json["geometry"]["coordinates"][0]
            bokeh_sea[0].append([coord[0] for coord in coord_list])
            bokeh_sea[1].append([coord[1] for coord in coord_list])

def load_from_pickle(path):

    poly_list = pickle.load(open(path, "rb"))

    # Unwrap the poly list
    vertex_group = list()
    for lats, longs in zip(poly_list[0], poly_list[1]):
        vertex_group.append(list(zip(lats, longs)))

    # return [[[100, 100], [100, 200], [200, 200], [200, 100]]]

    '''
    *
    |
    |
    |
    |
    |
    '''
    # return [[[1, 0], [2, 0], [2, 1]]]
    # return [[[1, 0], [2, 0], [2, 1]], [[1, 0.5], [1, 1], [1.5, 1]]]


    # biggest_4 = sorted(vertex_group)[:10]

    return vertex_group

def gen_river_poly(bounds, N=10, width_frac=0.4):

    """
    Create a simple river / channel like environment with no branches
    :param bounds:
    :param N:
    :return:
    """
    print("Generating riverbank polies for N =", N)
    delta = bounds[1] / (N)
    avg_width = int((1-width_frac)*bounds[0] / 2)

    print(avg_width)

    def river_bank_helper(n_segments, x_min, x_max):
        vs = [[x_min, 0]]
        x = random.randint(x_min, x_max)
        jitter_val = round((x_max - x_min) / 4)

        vs.append([x_min, 0])

        for i in range(1, n_segments):

            skip_jitter = int(i != 0 and i != n_segments)
            if not skip_jitter:
                y_jitter = random.randrange(round(-delta / 4), round(delta / 4))
            else:
                y_jitter = 0
            # y_jitter = 0
            y = round(delta * i + y_jitter)

            # width = int(avg_width / 2)

            x = random.randint(x - jitter_val, x + jitter_val)
            while x > x_max or x < x_min:
                x = random.randint(x - jitter_val, x + jitter_val)

            vs.append([x, y])

        print(f"Generated river bank poly with {len(vs)} vertices")
        return vs

    # Left side polygon

    # Make it slightly less symmetrical

    # left_vs = list([[0,0], [0, avg_width]])
    # left_vs.extend(river_bank(N, 0, 100))

    # close the loop
    # left_vs.append([0, bounds[1]])

    left_vs = river_bank_helper(N, 0, avg_width)
    left_vs.extend([[0, bounds[1]], [0,0]])

    right_vs = river_bank_helper(N, bounds[0] - avg_width, bounds[0])
    right_vs.extend([[bounds[0], bounds[1]], [bounds[0], 0]])

    # right_vs.append(bounds)
    # right_vs.append([bounds[0], 0])

    # right_vs.extend(river_bank(N))
    # for i in range(0, N + 1):
    #     y = delta * i
    #     width = avg_width / 2
    #     x = random.randint(bounds[0] - width, bounds[0])
    #
    #     right_vs.append([x, y])

    # close the loop
    # right_vs.append([bounds[0], bounds[1]])
    # right_vs.append([bounds[0], 0])

    return [left_vs, right_vs]