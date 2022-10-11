from ns import NS, BLDG_ATTRIB


class BldgGml:
    def __init__(self, city_obj):

        self.city_obj = city_obj

        self.ns = BLDG_ATTRIB()

        self.bldg_obj = None

        self.parent_id = ""
        self.id = ""
        self.usage = 0
        self.h = 0
        self.storey = 0
        self.details = {}

        self.l0_coords = []
        self.l1_coords = []

        self.tfa = 0

        self.extract_bldg_obj()
        self.extract_general_attrib()
        self.extract_coords()
        self.cal_tfa()

    def extract_bldg_obj(self):
        pass

    def extract_general_attrib(self):

        self.parent_id = ""
        self.id = ""
        self.usage = ""
        self.h = 0
        self.storey = 0
        self.details = 0

    def extract_coords(self):

        self.l0_coords = ""
        self.l1_coords = ""

    def cal_tfa(self):
        pass
