#%%
import xml.etree.ElementTree as ET

from mypath import *
from const import *
from ns import *


bldg_et = ET.parse(LIST_GMLS)

list_city_objs = bldg_et.findall("core:cityObjectMember//bldg:Building", NS)
# %%
