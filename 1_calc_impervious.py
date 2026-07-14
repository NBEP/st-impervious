# ---------------------------------------------------------------------------
# 1_calc_impervious.py
# Authors: Mariel Sorlien
# Python 3.11
#
# Description:
# Calculates percent impervious cover at seven different geoscales.
#
# REQUIRES GIS/ARCPY
# ---------------------------------------------------------------------------

# Import modules
from pathlib import Path
import arcpy
import pandas as pd
from functions import *

arcpy.env.overwriteOutput = True

# Set working directory, projection --------------------------------------------
base_folder = Path.cwd().parents[2] / "Data"
csv_folder = base_folder / "int_tabulardata" / "impervious_int"
arcpy.env.workspace = str(base_folder / "int_gisdata" / "impervious_int")

# Define INPUT - FRACTIONAL IMPERVIOUS SURFACE
impervious_year = 2025
impervious_raster = "Annual_NLCD_FctImp_" + str(impervious_year) + "_CU_C1V2.tif"

# Define INPUT - GEOSCALES
# Download from https://narragansett-bay-estuary-program-nbep.hub.arcgis.com/
geoscale_folder = base_folder / "int_gisdata" / "geoscale_int" / "geoscale_int.gdb"

studyarea = str(geoscale_folder / "STUDYAREAS_NBEP2017")
basins = str(geoscale_folder / "BASINS_NBEP2017")
huc10 = str(geoscale_folder / "HUC10_NBEP2017")
huc12 = str(geoscale_folder / "HUC12_NBEP2017")
state_studyarea = str(geoscale_folder / "STATES_ByStudyArea_NBEP2017")
town = str(geoscale_folder / "TOWNS_NBEP2017")
town_studyarea = str(geoscale_folder / "TOWNS_ByStudyArea_NBEP2017")
bay = str(geoscale_folder / "BAYS_NBEP2017")

# Define OUTPUTS
nlcd_final = "impervious_int.gdb/IMPERVIOUS_" + str(impervious_year) + "_NBEP2026"
csv_final = "IMPERVIOUS_" + str(impervious_year) + "_NBEP2026.csv"

# RUN SCRIPT ----------------------------------------------------------------------------------------------------------
temp_union = arcpy.env.scratchFolder + "/temp_union.shp"
temp_buffer = arcpy.env.scratchFolder + "/temp_buffer.shp"
temp_clip = arcpy.env.scratchFolder + "/temp_boundaries.shp"
temp_shp = arcpy.env.scratchFolder + "/temp_shp.shp"
temp_impervious = arcpy.env.scratchFolder + "/temp_impervious.tif"
temp_raster = arcpy.env.scratchFolder + "/temp_raster.tif"

print("\nSETTING DEFAULT VALUES")
print("Setting snap raster")
arcpy.env.snapRaster = impervious_raster
print("Retrieving NLCD spatial reference")
spatial_ref = arcpy.Describe(impervious_raster).spatialReference

print("\nPROCESSING", impervious_year, "IMPERVIOUS DATA")
print("Setting clip boundaries")
print("\tMerging town and bay boundaries")
arcpy.analysis.Union(
    in_features=[town, bay],
    out_feature_class=temp_union
)
print("\tAdding 30m buffer")
arcpy.analysis.Buffer(
    in_features=temp_union,
    out_feature_class=temp_buffer,
    buffer_distance_or_field="30 Meters",
    dissolve_option="ALL"
)
print("\tProjecting to Albers")
arcpy.management.Project(
    in_dataset=temp_buffer,
    out_dataset=temp_clip,
    out_coor_system=spatial_ref
)
print("Clipping impervious cover")
arcpy.management.Clip(
    in_raster=impervious_raster,
    in_template_dataset=temp_clip,
    out_raster=temp_impervious
)

print("\nCALCULATING AREA")
print("Per study area")
df_acres = calc_stats.calc_percent(
    in_geoscale=studyarea,
    geoscale_field="Study_Area",
    in_raster=temp_impervious,
    raster_year=impervious_year
)
df_acres.rename(columns={"Geoscale_Name": "Study_Area"}, inplace=True)

print("Per basin")
df_temp = calc_stats.calc_percent(
    in_geoscale=basins,
    geoscale_field="Basins",
    in_raster=temp_impervious,
    raster_year=impervious_year
)
df_temp = prep_csv.add_study_area(
    df=df_temp,
    geoscale_field="Basins",
    ref_csv="data/basin.csv"
)
df_acres = pd.concat([df_acres, df_temp])

print("Per HUC10")
df_temp = calc_stats.calc_percent(
    in_geoscale=huc10,
    geoscale_field="HUC10",
    in_raster=temp_impervious,
    raster_year=impervious_year
)
df_temp = prep_csv.add_study_area(
    df=df_temp,
    geoscale_field="HUC10",
    ref_csv="data/HUC10.csv"
)
df_acres = pd.concat([df_acres, df_temp])

print("Per HUC12")
df_temp = calc_stats.calc_percent(
    in_geoscale=huc12,
    geoscale_field="HUC12",
    in_raster=temp_impervious,
    raster_year=impervious_year
)
df_temp = prep_csv.add_study_area(
    df=df_temp,
    geoscale_field="HUC12",
    ref_csv="data/HUC12.csv"
)
df_acres = pd.concat([df_acres, df_temp])

print("Per state per study area")
update_field.merge_field(
    in_table=state_studyarea,
    out_table=temp_shp,
    new_field="State_Area",
    expression='!State! + "-" + !Study_Area!'
)
df_temp = calc_stats.calc_percent(
    in_geoscale=temp_shp,
    geoscale_field="State_Area",
    in_raster=temp_impervious,
    raster_year=impervious_year
)
df_temp[["State", "Study_Area"]] = df_temp["Geoscale_Name"].str.split("-", expand=True)
df_acres = pd.concat([df_acres, df_temp])

print("Per town")
update_field.merge_field(
    in_table=town,
    out_table=temp_shp,
    new_field="Town_State",
    expression='!Town_Name! + "-" + !State!'
)
df_temp = calc_stats.calc_percent(
    in_geoscale=temp_shp,
    geoscale_field="Town_State",
    in_raster=temp_impervious,
    raster_year=impervious_year
)
df_temp[["Town", "State"]] = df_temp["Geoscale_Name"].str.split("-", expand=True)
df_acres = pd.concat([df_acres, df_temp])

print("Per town per study area")
update_field.merge_field(
    in_table=town_studyarea,
    out_table=temp_shp,
    new_field="Town_Area",
    expression='!Town_Name! + "-" + !State! + "-" + !Study_Area!'
)
df_temp = calc_stats.calc_percent(
    in_geoscale=temp_shp,
    geoscale_field="Town_Area",
    in_raster=temp_impervious,
    raster_year=impervious_year
)
df_temp[["Town", "State", "Study_Area"]] = df_temp["Geoscale_Name"].str.split("-", expand=True)
df_acres = pd.concat([df_acres, df_temp])

print("Updating columns")
df_acres.replace(
    to_replace={
        "State": {
            "CT": "Connecticut", "CONNECTICUT": "Connecticut",
            "RI": "Rhode Island", "RHODE ISLAND": "Rhode Island",
            "MA": "Massachusetts", "MASSACHUSETTS": "Massachusetts", "MASSACHUSSETTS": "Massachusetts"
        }
    },
    inplace=True
)
df_acres = df_acres[[
    "Geoscale", "Geoscale_Name", "Town", "State", "HUC10", "HUC10_Name", "HUC12", "HUC12_Name", "Basins", "Study_Area",
    "Year", "Percent_Impervious", "Acres_Impervious", "Acres_Total"
]]

print("\nDOWNLOADING FILES")
print("Saving csv")
df_acres.to_csv(csv_folder / csv_final, index=False)

print("Saving raster")
print("\tProjecting to UTM Zone 19N NAD 1983")
arcpy.management.ProjectRaster(
    in_raster=temp_impervious,
    out_raster=temp_raster,
    out_coor_system=arcpy.SpatialReference("NAD 1983 UTM Zone 19N")
)
print("\tClipping data")
arcpy.management.Clip(
    in_raster=temp_raster,
    out_raster=nlcd_final,
    in_template_dataset=temp_buffer,
    clipping_geometry="ClippingGeometry"
)

print("\nCLEARING SCRATCH FOLDER")
arcpy.management.Delete([temp_union, temp_buffer, temp_clip, temp_shp, temp_impervious, temp_raster])

print("\nDONE")
