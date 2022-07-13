# Name: LND_Schedule_Change.py
# Description: Add field and domain to LND_Schedule Table
# Author: Peter Miles

# Import system modules
import arcpy
import os
import sys
import time
from arcpy import env
from datetime import datetime
arcpy.SetLogHistory(False)

# Print start time
s = datetime.now()
print(s.strftime('%Y/%m/%d %H:%M:%S'))


def xxx(command):
    command
    print(arcpy.GetMessages(0))
    print('-' * 100)


#GDB_Name = r"T:\monthly\202204apr\milesp\01_GIS_Change\01_Grass\Scratch.gdb"
#GDB_Name = "C:\\Users\\milesp\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\SDEADM_DEV_GIS_HRM_RW_Win.sde"
#GDB_Name = "C:\\Users\\milesp\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\SDEADM_DEV_GIS_HRM_RO_Win.sde"
#GDB_Name = r"\\msfs06\GISApp\AGS_Dev\fgdbs\web_RO.gdb"
#GDB_Name = "C:\\Users\\milesp\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\webgis_DEV_GIS_HRM_RO_win.sde"
       
#GDB_Name = "C:\\Users\\milesp\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\SDEADM_QA_GIS_HRM_RW_Win.sde"
#GDB_Name = "C:\\Users\\milesp\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\SDEADM_QA_GIS_HRM_RO_Win.sde"
#GDB_Name = r"\\msfs06\GISApp\AGS_QA107\fgdbs\web_RO.gdb"
#GDB_Name = "C:\\Users\\milesp\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\webgis_QA_GIS_HRM_RO_win.sde"
    
#GDB_Name = "C:\\Users\\milesp\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\SDEADM_PROD_GIS_HRM_RW_Win.sde"
#GDB_Name = "C:\\Users\\milesp\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\SDEADM_PROD_GIS_HRM_RO_Win.sde"
#GDB_Name = r"\\msfs06\GISApp\AGS_Prod107\fgdbs\web_RO.gdb"
GDB_Name = "C:\\Users\\milesp\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\webgis_PROD_GIS_HRM_RO_win.sde"

# Feature Class
grass_feature = "LND_grass_contract"

# New Domains
Grass_Class = "LND_grass_class"

print(GDB_Name)

print("Create new domains")
xxx(arcpy.management.CreateDomain(GDB_Name, Grass_Class, "Grass Contract Class", "TEXT", "CODED", "DUPLICATE", "DEFAULT"))

print("Add coded domain values..." + Grass_Class)
xxx(arcpy.AddCodedValueToDomain_management(GDB_Name, Grass_Class, "A", "A Class"))
xxx(arcpy.AddCodedValueToDomain_management(GDB_Name, Grass_Class, "B", "B Class"))
xxx(arcpy.AddCodedValueToDomain_management(GDB_Name, Grass_Class, "C", "C Class"))


# print ("Modify Schema on..." + Grass)
# xxx (arcpy.management.AddField(GDB_Name + "\\" + Grass, "SERCLASS", "TEXT", "", "", "2", "Service Classification", "", "", "LND_grass_class"))
# xxx (arcpy.management.AddField(GDB_Name + "\\" + Grass, "COMMENTS", "TEXT", "", "", "250", "Grass Comment", "", "", ""))
# xxx (arcpy.management.AlterField(GDB_Name + "\\" + Grass, "SERCLASS", "#", "Service Classification"))


# print end time
f = datetime.now()
print (f.strftime('%Y/%m/%d %H:%M:%S'))
