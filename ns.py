GML_NS = {
    "bldg": "http://www.opengis.net/citygml/building/2.0",
    "core": "http://www.opengis.net/citygml/2.0",
    "gml": "http://www.opengis.net/gml",
    "uro": "http://www.kantei.go.jp/jp/singi/tiiki/toshisaisei/itoshisaisei/iur/uro/1.4",
}


class BLDG_ATTRIB:
    def __init__(self):

        self.bldg = "core:cityObjectMember//bldg:Building"
        self.bldg_part = "bldg:consistsOfBuildingPart//bldg:BuildingPart"
        self.usage = "bldg:usage"
        self.h = "bldg:measuredHeight"
        self.l0_coords = "bldg:lod0FootPrint//gml:posList"
        self.l1_coords = "bldg:lod1Solid//gml:posList"
        self.l2 = "bldg:lod2Solid"
        self.storey = "bldg:storeysAboveGround"
        self.details = "uro:buildingDetails//uro:BuildingDetails"
        # self.roof_edge = (
        #     "uro:buildingDetails//uro:BuildingDetails//uro:buildingRoofEdgeArea"
        # )
        # self.prefecture = "uro:buildingDetails//uro:BuildingDetails//uro:prefecture"
        # self.city = "uro:buildingDetails//uro:BuildingDetails//uro:city"
        # self.surveyYear = "uro:buildingDetails//uro:BuildingDetails//uro:surveyYear"


# class BuildingXML:
#     def __init__(self):

#         self.usageDes = "gml:dictionaryEntry//gml:Definition//gml:description"
#         self.usageId = "gml:dictionaryEntry//gml:Definition//gml:name"
