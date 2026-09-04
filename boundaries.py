import json
import geopandas as gpd

from weather_codes import get_weather_info

LAD_BOUNDARY_PATH = "data/LAD_major_city_boundary_data.gpkg"
LAD_NAME_FIELD = "LAD25NM"


def load_lad_layer_wgs84():
    layer = gpd.read_file(LAD_BOUNDARY_PATH)
    if layer.crs is not None and layer.crs.to_epsg() != 4326:
        layer = layer.to_crs(epsg=4326)
    return layer
