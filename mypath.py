#%%
import os
import glob


def get_path_cee(year):
    csv_mesh_dir = rf"D:\Emission Data\Tanikawa-sensei data\takeuhi_pro\takeuhi_pro\消費支出推計メッシュデータ{year}"
    cee_csv = f"消費支出推計MESH{year}W4_03光熱水道.csv"
    return os.path.join(csv_mesh_dir, cee_csv)


JP_500M_SHP = r"D:\SHP\japan-500m-mesh\merge\jp_500m_mesh.shp"
CEE_500M_CSV_2020 = get_path_cee(2020)
CEE_500M_CSV_2019 = get_path_cee(2019)

CITYGML_DIR = r"F:\3d_plateau\23100_nagoya-shi_2020_citygml_4_op\udx\bldg"
LIST_GMLS = glob.glob(os.path.join(CITYGML_DIR, "*.gml"))

LIST_FOLDER = glob.glob("F:/3d_plateau/*/")

DATA_DIR = "data"

CITY_BOUND_DIR = os.path.join(DATA_DIR, "bound")
JP_CEE_DIR = os.path.join(DATA_DIR, "cee", "japan")
TEMP_DIR = os.path.join(DATA_DIR, "temp", "japan")

# %%
