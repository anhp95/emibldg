#%%
import pandas as pd
import geopandas as gpd
import os
import rasterio
import numpy as np
import calendar

from sklearn.preprocessing import MinMaxScaler
from rasterio.mask import mask

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

        self.grid_unit = []
        self.train = None

        self._extract_bound()
        self._clip_cee_df()
        self._get_ref_files()

        self._cal_grid_unit()
        self._extract_train()

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
            self.grid_unit.append(
                GridUnit(
                    self.cee_df.iloc[i],
                    self.city_3d_df,
                    self.list_temp_tif,
                    self.pop_df,
                    self.year,
                ).grid_df
            )

    def _extract_train(self):
        city_df = pd.concat(self.grid_unit, axis=0, ignore_index=True)
        other_col_cal = {
            "electric": "sum",
            "city_gas": "sum",
            "kerosene": "sum",
            "propane": "sum",
            "total_area": "sum",
            "avg_height": "mean",
            "rp_14": "mean",
            "rp_1565": "mean",
            "rp_75": "mean",
        }
        temp_col_cal = {calendar.month_name[i]: "mean" for i in range(1, 13)}
        col_cal = other_col_cal | temp_col_cal
        df_train = city_df.groupby("target_grid_id").agg(col_cal)

        df_train = df_train[df_train["total_area"] >0]
        df_train = df_train[df_train["January"]>0]
        df_train = df_train[df_train["electric"]>0]

        self.train = df_train
    
    def preprocess_train(self):
        
        cols = self.train.columns

        scaler_x = MinMaxScaler()

        scaler_e = MinMaxScaler()
        scaler_gas = MinMaxScaler()
        scaler_kerosene = MinMaxScaler()
        scaler_propane = MinMaxScaler()

        e = scaler_e.fit_transform(self.train["electric"].values.reshape(-1,1))
        gas = scaler_gas.fit_transform(self.train["gcity_gas"].values.reshape(-1,1))
        kerosene = scaler_kerosene.fit_transform(self.train["kerosene"].values.reshape(-1,1))
        propane = scaler_propane.fit_transform(self.train["propane"].values.reshape(-1,1))

        x = scaler_x.fit_transform(self.train[cols[4:]].values)

        scaler_dict = {
            "electric": scaler_e,
            "gas": scaler_gas,
            "kerosene": scaler_kerosene,
            "propane": scaler_propane,
            "x": scaler_x
        }

        data_dict = {
            "electric": e,
            "gas": gas,
            "kerosene": kerosene,
            "propane": propane,
            "x": x,
        }

        return data_dict, scaler_dict

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

        self.temp = []

        self.rp_14 = 0
        self.rp_1565 = 0
        self.rp_75 = 0

        self.grid_df = pd.DataFrame()

        self._extract_energy(cee_row)
        self._extract_bldg_attrib(cee_row, city_3d_df)
        self._extract_temp(cee_row, list_temp_tif)
        self._extract_pop(pop_df)
        self._to_df()

    def _extract_energy(self, cee_row):

        self.grid_id = cee_row["mesh_code"]
        self.target_grid_id = (
            cee_row["mesh_t"]
            if not pd.isna(cee_row["mesh_t"])
            else cee_row["mesh_code"]
        )
        self.electric = cee_row["e_f"]
        self.city_gas = cee_row["g_shi"]
        self.propane = cee_row["g_prop"]
        self.kerosene = cee_row["kerosene"]
        self.geometry = cee_row["geometry"]

    def _cal_co2(self):
        pass

    def _extract_bldg_attrib(self, cee_row, city_3d_df):
        pol = cee_row["geometry"]
        grid_3d_df = city_3d_df[city_3d_df["geometry"].apply(pol.contains)].copy()
        self.total_area = (grid_3d_df["h"] * grid_3d_df["l0_area"]).sum()
        self.avg_height = grid_3d_df["h"].mean()

    def _extract_temp(self, cee_row, list_temp_tif):

        for img in list_temp_tif:
            out_img, _ = mask(img, [cee_row["geometry"]], crop=True)
            masked_zero = out_img[out_img > 0]
            self.temp.append(np.mean(masked_zero))

    def _extract_pop(self, pop_df):
        grid_pop_df = pop_df.loc[pop_df["MESH_ID"] == self.grid_id]
        self.rp_14 = grid_pop_df[f"RTA_{self.year}"].item()
        self.rp_1565 = grid_pop_df[f"RTB_{self.year}"].item()
        self.rp_75 = (
            grid_pop_df[f"RTC_{self.year}"].item()
            + grid_pop_df[f"RTD_{self.year}"].item()
            + grid_pop_df[f"RTE_{self.year}"].item()
        )

    def _to_df(self):

        self.grid_df["grid_id"] = [self.grid_id]
        self.grid_df["target_grid_id"] = [self.target_grid_id]
        self.grid_df["geometry"] = [self.geometry]

        self.grid_df["electric"] = [self.electric]
        self.grid_df["city_gas"] = [self.city_gas]
        self.grid_df["kerosene"] = [self.kerosene]
        self.grid_df["propane"] = [self.propane]

        self.grid_df["co2"] = [self.co2]

        self.grid_df["total_area"] = [self.total_area]
        self.grid_df["avg_height"] = [self.avg_height]

        for i in range(1, 13):
            self.grid_df[calendar.month_name[i]] = [self.temp[i - 1]]

        self.grid_df["rp_14"] = [self.rp_14]
        self.grid_df["rp_1565"] = [self.rp_1565]
        self.grid_df["rp_75"] = [self.rp_75]


# %%
a = CeeCityMesh("nagoya", 2020)
