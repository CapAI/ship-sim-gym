# From dashboard/visualizer:
import json
import pickle

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

