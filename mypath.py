#%%
import os
import glob


CSV_MESH_DIR = (
    r"D:\Emission Data\Tanikawa-sensei data\takeuhi_pro\takeuhi_pro\消費支出推計メッシュデータ"
)

CEE_NAME_CSV = "消費支出推計MESH2020W4_03光熱水道.csv"


JP_500M_SHP = r"D:\SHP\japan-500m-mesh\merge\jp_500m_mesh.shp"
CEE_500M_CSV_2020 = os.path.join(f"{CSV_MESH_DIR}2020", CEE_NAME_CSV)
CEE_500M_CSV_2019 = os.path.join(f"{CSV_MESH_DIR}2019", CEE_NAME_CSV)

CITYGML_DIR = r"F:\3d_plateau\23100_nagoya-shi_2020_citygml_4_op\udx\bldg"
LIST_GMLS = glob.glob(os.path.join(CITYGML_DIR, "*.gml"))[1]
# %%
