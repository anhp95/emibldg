#%%
import pandas as pd
import geopandas as gpd
import os
import rasterio
from rasterio.mask import mask

from matplotlib import pyplot
from mypath import *


class CeeCityMesh:
    def __init__(self, city, year) -> None:

        self.city = city
        self.year = year

        self.bound_df = None

        self.cee_df = None
        self.grid = []

        self._extract_bound()
        self._clip_cee_df()
        # self._cal_grid_unit()

    def _extract_bound(self):

        bounds_shp = os.path.join(CITY_BOUND_DIR, f"{self.city}.shp")
        bound_df = gpd.read_file(bounds_shp)

        self.bound_df = bound_df

    def _clip_cee_df(self):

        cee_shp = os.path.join(JP_CEE_DIR, f"{self.year}.shp")
        cee_df = gpd.read_file(cee_shp)
        # self.cee_df = gpd.clip(cee_df, self.bound, keep_geom_type=True)
        self.cee_df = gpd.sjoin(cee_df, self.bound_df, how="inner")

    def _cal_grid_unit(self):
        for i in range(0, len(self.cee_df)):
            self.grid.append(GridUnit(self.cee_df.iloc[i], self.year))


class GridUnit:
    def __init__(self, df_row, year) -> None:

        self.year = year

        self.grid_id = 0
        self.target_grid_id = ""
        self.geometry = None
        self.electric = 0
        self.city_gas = 0
        self.kerosene = 0
        self.propane = 0

        self.co2 = 0

        self.total_area = 0
        self.avg_height = 0

        self.temp = ""

        self.rp_14 = 0
        self.rp_1565 = 0
        self.rp_75 = 0

        self._extract_energy(df_row)
        self._extract_temp()

    def _extract_energy(self, df_row):

        self.grid_id = df_row["mesh_code"]
        self.target_grid_id = df_row["mesh_t"]
        self.electric = df_row["e_f"]
        self.city_gas = df_row["g_shi"]
        self.propane = df_row["g_prop"]
        self.kerosene = df_row["kerosene"]
        self.geometry = df_row["geometry"]

    def _cal_co2(self):
        pass

    def _extract_bldg_attrib(self):
        pass

    def _extract_temp(self):
        list_tif = sorted(glob.glob(os.path.join(TEMP_DIR, f"{self.year}*")))

        for tif in list_tif:
            img = rasterio.open(tif)
            out_image, _ = mask(img, self.geometry.geometry, crop=True)
            pyplot.imshow(out_image, cmap="pink")
            pyplot.show()

    def _extract_pop(self):
        pass


# %%
a = CeeCityMesh("nagoya", 2020)
list_tif = sorted(glob.glob(os.path.join(TEMP_DIR, f"2020*")))
tif = list_tif[0]
img = rasterio.open(tif)
out_image, _ = mask(img, a.cee_df.iloc[0].geometry, crop=True)
pyplot.imshow(out_image, cmap="pink")
pyplot.show()