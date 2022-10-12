#%%
import xml.etree.ElementTree as ET
from shapely.geometry import Polygon

from ns import GML_NS, BLDG_ATTRIB
from mypath import LIST_GMLS

BLDG_NS = BLDG_ATTRIB()


class CityObj:
    def __init__(self, city_obj) -> None:
        self.city_obj = city_obj
        self.city_obj_mem = []

        self._extract_city_obj_mem()

    def _extract_city_obj_mem(self):
        city_obj_mem = self.city_obj.findall(BLDG_NS.bldg, GML_NS)

        for bldg_obj in city_obj_mem:
            self.city_obj_mem.append(BldgObj(bldg_obj))


class BldgObj:
    def __init__(self, bldg_obj) -> None:

        self.bldg_obj = bldg_obj

        self.bldg_id = ""

        self.no_bldg_part = 0
        self.bldg_part = []

        self._get_bldg_id()
        self._extract_bldg_part()

    def _get_bldg_id(self):

        self.bldg_id = list(self.bldg_obj.attrib.values())[0]

    def _extract_bldg_part(self):
        bldg_parts = self.bldg_obj.findall(BLDG_NS.bldg_part, GML_NS)

        self.no_bldg_part = len(bldg_parts)

        if self.no_bldg_part > 0:
            for bp_obj in bldg_parts:
                self.bldg_part.append(BldgPartObj(self.bldg_id, bp_obj))
        else:
            self.bldg_part.append(BldgPartObj(self.bldg_id, self.bldg_obj))


class BldgPartObj:
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

        self.tfa = 0

        self._extract_id()
        self._extract_usage()
        self._extract_storey()
        self._extract_details()
        self._extract_geometry_height()
        # self._cal_tfa()

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

        for child in details:
            self.details[child.tag.replace(self.uro_url, "")] = child.text

    def _extract_geometry_height(self):

        l0_coords = self.bldg_part_obj.find(BLDG_NS.l0_coords, GML_NS)
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
            lat.append(l0_coords[i + 1])

        self.geometry = Polygon(zip(lon, lat))

    def _extract_height(self):
        h = self.bldg_part_obj.find(BLDG_NS.h, GML_NS)
        self.h = float(h.text) if h is not None else 0

    # def cal_tfa(self):
    #     pass


# %%
a = ET.parse(LIST_GMLS)
cityobj = CityObj(a)

# %%
