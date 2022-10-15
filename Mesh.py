#%%
import pandas as pd
import geopandas as gpd
import os
import rasterio
import numpy as np

from rasterio.mask import mask

from matplotlib import pyplot
from mypath import *


class CeeCityMesh:
    def __init__(self, city, year) -> None:

        self.city = city
        self.year = year

        self.bound_df = None

        self.cee_df = None

        self.pop_df = None
        self.city_3d_df = None
        self.list_temp_tif = []

        self.grid = []

        self._extract_bound()
        self._clip_cee_df()
        self._get_ref_files()
        self._cal_grid_unit()

    def _extract_bound(self):

        bounds_shp = os.path.join(CITY_BOUND_DIR, f"{self.city}.shp")
        bound_df = gpd.read_file(bounds_shp)

        self.bound_df = bound_df

    def _clip_cee_df(self):

        cee_shp = os.path.join(JP_CEE_DIR, f"{self.year}.shp")
        cee_df = gpd.read_file(cee_shp)
        # self.cee_df = gpd.clip(cee_df, self.bound, keep_geom_type=True)
        self.cee_df = gpd.sjoin(cee_df, self.bound_df, how="inner")

    def _get_ref_files(self):

        city_3d_shp = os.path.join(SHP_3D_DIR, self.city, f"{self.city}.shp")
        self.city_3d_df = gpd.read_file(city_3d_shp)

        list_temp_tif = sorted(glob.glob(os.path.join(TEMP_DIR, f"{self.year}*")))
        for temp in list_temp_tif:
            self.list_temp_tif.append(rasterio.open(temp))

        pop_df = gpd.read_file(POP_SHP)
        cols = [
            "MESH_ID",
            f"RTA_{self.year}",
            f"RTB_{self.year}",
            f"RTC_{self.year}",
            f"RTD_{self.year}",
            f"RTE_{self.year}",
        ]
        self.pop_df = gpd.sjoin(pop_df, self.bound_df, how="inner")[cols]

    def _cal_grid_unit(self):
        for i in range(0, len(self.cee_df)):
            self.grid.append(
                GridUnit(
                    self.cee_df.iloc[i],
                    self.city_3d_df,
                    self.list_temp_tif,
                    self.pop_df,
                    self.year,
                )
            )


class GridUnit:
    def __init__(self, cee_row, city_3d_df, list_temp_tif, pop_df, year) -> None:
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
        self.grid_3d_df = []

        self.temp = []

        self.rp_14 = 0
        self.rp_1565 = 0
        self.rp_75 = 0

        self._extract_energy(cee_row)
        self._extract_bldg_attrib(cee_row, city_3d_df)
        # self._extract_temp(cee_row, list_temp_tif)
        # self._extract_pop(pop_df)

    def _extract_energy(self, cee_row):

        self.grid_id = cee_row["mesh_code"]
        self.target_grid_id = cee_row["mesh_t"]
        self.electric = cee_row["e_f"]
        self.city_gas = cee_row["g_shi"]
        self.propane = cee_row["g_prop"]
        self.kerosene = cee_row["kerosene"]
        self.geometry = cee_row["geometry"]

    def _cal_co2(self):
        pass

    def _extract_bldg_attrib(self, cee_row, city_3d_df):
        pol = cee_row["geometry"]
        grid_3d = city_3d_df[city_3d_df["geometry"].apply(pol.contains)].copy()
        self.total_area = (grid_3d["h"] * grid_3d["l0_area"]).sum()
        self.avg_height = grid_3d["h"].mean()
        # self.grid_3d_df.append()
        # self.grid_3d_df = grid_3d_df

    def _extract_temp(self, cee_row, list_temp_tif):
        # list_tif = sorted(glob.glob(os.path.join(TEMP_DIR, f"{self.year}*")))

        for img in list_temp_tif:
            # img = rasterio.open(tif)
            out_img, _ = mask(img, [cee_row["geometry"]], crop=True)
            masked_zero = out_img[out_img > 0]
            self.temp.append(np.mean(masked_zero))

    def _extract_pop(self, pop_df):
        # pop_df = gpd.read_file(POP_SHP)
        grid_pop_df = pop_df.loc[pop_df["MESH_ID"] == self.grid_id]
        self.rp_14 = grid_pop_df[f"RTA_{self.year}"].item()
        self.rp_1565 = grid_pop_df[f"RTB_{self.year}"].item()
        self.rp_75 = (
            grid_pop_df[f"RTC_{self.year}"].item()
            + grid_pop_df[f"RTD_{self.year}"].item()
            + grid_pop_df[f"RTE_{self.year}"].item()
        )


# %%
a = CeeCityMesh("nagoya", 2020)
# list_tif = sorted(glob.glob(os.path.join(TEMP_DIR, f"2020*")))
# tif = list_tif[0]
# img = rasterio.open(tif)
# out_image, _ = mask(img, [a.cee_df.iloc[0].geometry], crop=True)
# _, y, x = out_image.shape
# out_image = out_image.reshape(x,y)
# pyplot.imshow(out_image, cmap="pink")
# pyplot.show()
# %%
