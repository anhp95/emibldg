#%%
import xml.etree.ElementTree as ET
import pandas as pd
import geopandas as gpd

from pyproj import Geod
from shapely.geometry import Polygon

from ns import GML_NS, BLDG_ATTRIB
from mypath import LIST_GMLS

BLDG_NS = BLDG_ATTRIB()


class CityObj:
    def __init__(self, city_obj) -> None:
        self.city_obj = city_obj
        self.city_obj_mem = []

        self.all_bldg_pars = None

        self._extract_city_obj_mem()
        self._extract_all_bldg_parts_gpd_df()

    def _extract_city_obj_mem(self):
        city_obj_mem = self.city_obj.findall(BLDG_NS.bldg, GML_NS)

        for bldg_obj in city_obj_mem:
            self.city_obj_mem.append(BldgObj(bldg_obj))

    def _extract_all_bldg_parts_gpd_df(self):
        df = gpd.GeoDataFrame()

        for bldg_obj in self.city_obj_mem:
            for bldg_part in bldg_obj.bldg_parts:
                # bldg_parts.append(bldg_part.gpd_df)
                df = pd.concat([df, bldg_part.gpd_df], axis=0, ignore_index=True)
        self.all_bldg_pars = gpd.GeoDataFrame(df)

        # df = df.set_geometry("geometry")
        # df.to_file(filename="test_shp.shp")


class BldgObj:
    def __init__(self, bldg_obj) -> None:

        self.bldg_obj = bldg_obj

        self.bldg_id = ""

        self.no_bldg_part = 0
        self.bldg_parts = []

        self._get_bldg_id()
        self._extract_bldg_part()

    def _get_bldg_id(self):

        self.bldg_id = list(self.bldg_obj.attrib.values())[0]

    def _extract_bldg_part(self):
        bldg_parts = self.bldg_obj.findall(BLDG_NS.bldg_part, GML_NS)

        self.no_bldg_part = len(bldg_parts)

        if self.no_bldg_part > 0:
            for bp_obj in bldg_parts:
                self.bldg_parts.append(BldgPartObj(self.bldg_id, bp_obj))
        else:
            self.bldg_parts.append(BldgPartObj(self.bldg_id, self.bldg_obj))


class BldgPartObj:

    crs = {"proj": "latlong", "ellps": "WGS84", "datum": "WGS84", "no_defs": True}
    uro_url = f'{{{GML_NS["uro"]}}}'

    def __init__(self, parent_id, bldg_part_obj):

        self.parent_id = parent_id
        self.bldg_part_obj = bldg_part_obj

        self.id = ""
        self.usage = 0
        self.h = 0
        self.storey = 0
        self.details = {}

        self.geometry = []

        self.gpd_df = None

        self.l0_area = 0

        self._extract_id()
        self._extract_usage()
        self._extract_storey()
        self._extract_details()
        self._extract_geometry_height()
        self._cal_l0_area()
        self._to_gpd_df()

    def _extract_id(self):
        self.id = list(self.bldg_part_obj.attrib.values())[0]

    def _extract_usage(self):

        usage = self.bldg_part_obj.find(BLDG_NS.usage, GML_NS)
        self.usage = int(usage.text) if usage is not None else 0

    def _extract_storey(self):
        storey = self.bldg_part_obj.find(BLDG_NS.storey, GML_NS)
        self.storey = int(storey.text) if storey is not None else 0

    def _extract_details(self):
        details = self.bldg_part_obj.find(BLDG_NS.details, GML_NS)
        if details is not None:
            for child in details:
                self.details[child.tag.replace(self.uro_url, "")] = child.text

    def _extract_geometry_height(self):

        l0_coords = self.bldg_part_obj.find(BLDG_NS.l0_coords_footprint, GML_NS)

        l0_coords = (
            l0_coords
            if l0_coords is not None
            else self.bldg_part_obj.find(BLDG_NS.l0_coords_roofedge, GML_NS)
        )

        l1_coords = self.bldg_part_obj.findall(BLDG_NS.l1_coords, GML_NS)

        h = self.bldg_part_obj.find(BLDG_NS.h, GML_NS)
        self.h = (
            float(h.text)
            if h is not None
            else (
                float(l1_coords[-1].text.split(" ")[2])
                - float(l0_coords.text.split(" ")[2])
            )
        )

        lat = []
        lon = []

        l0_coords = [float(x) for x in l0_coords.text.split(" ")]

        for i in range(0, len(l0_coords) - 3, 3):
            lat.append(l0_coords[i])
            lon.append(l0_coords[i + 1])

        self.geometry = Polygon(zip(lon, lat))
        self.l0_coords = l0_coords
        self.lat = lat
        self.lon = lon

    def _cal_l0_area(self):
        geod = Geod(ellps="WGS84")
        self.l0_area = abs(geod.geometry_area_perimeter(self.geometry)[0])

    def _to_gpd_df(self):
        df_dict = {}

        df_dict["parent_id"] = self.parent_id
        df_dict["id"] = self.id
        df_dict["usage"] = self.usage
        df_dict["h"] = self.h
        df_dict["storey"] = self.storey
        df_dict["l0_area"] = self.l0_area

        for k in self.details.keys():
            df_dict[k] = self.details[k]

        self.gpd_df = gpd.GeoDataFrame(
            df_dict, crs=self.crs, geometry=[self.geometry], index=[0]
        )


#%%

cityobj_bldg_parts = []
for i, gml in enumerate(LIST_GMLS):

    cityobj = CityObj(ET.parse(gml))
    cityobj_bldg_parts.append(cityobj.all_bldg_pars)
    print(i)

cityobj_df = pd.concat(cityobj_bldg_parts, axis=0, ignore_index=True)
cityobj_df = gpd.GeoDataFrame(cityobj_df)

cityobj_df.to_file(filename="nagoya2.shp")
# a = ET.parse(LIST_GMLS)
# cityobj = CityObj(a)

# %%
