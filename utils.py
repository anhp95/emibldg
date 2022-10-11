#%%
import geopandas as gpd
import pandas as pd

from mypath import *
from const import *


def merge_csv_shp(shp_path, csv_path):
    shp_df = gpd.read_file(shp_path)
    csv_df = pd.read_csv(csv_path, encoding=ENCODING)
    csv_df.columns = CEE_TRANS_COLS

    merge_df = shp_df.merge(csv_df, on="mesh_code")

    return merge_df


# %%
