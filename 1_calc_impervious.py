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

# Define INPUTS
impervious_year = 2025
impervious_raster = "Annual_NLCD_FctImp_" + str(impervious_year) + "_CU_C1V2.tif"

clip_boundaries = "impervious_int.gdb/geoscales/town_and_bay"

basins = "impervious_int.gdb/geoscales/BASINS_NBEP2017"
basins_field = "Basin"

huc10 = "impervious_int.gdb/geoscales/HUC10_NBEP2017"
huc10_field = "HUC10_Name"

huc12 = "impervious_int.gdb/geoscales/HUC12_NBEP2017"
huc12_field = "HUC12"  # Must include ID, since multiple HUC12 with same name

studyarea = "impervious_int.gdb/geoscales/STUDYAREAS_NBEP2017"
studyarea_field = "Study_Area"

state_studyarea = "impervious_int.gdb/geoscales/states_by_studyarea"
state_field = "State_Area"  # Must include state AND study area

town = "impervious_int.gdb/geoscales/town_and_bay"
town_field = "Town_State"  # Must include town AND state

town_studyarea = "impervious_int.gdb/geoscales/towns_by_studyarea"
town_studyarea_field = "Town_Area"  # Must include town, state, AND study area

# Define OUTPUTS
nlcd_final = "impervious_int.gdb/IMPERVIOUS_" + str(impervious_year) + "_NBEP2026"
csv_final = "IMPERVIOUS_" + str(impervious_year) + "_NBEP2026.csv"

# RUN SCRIPT ----------------------------------------------------------------------------------------------------------
temp_buffer = arcpy.env.scratchFolder + "/temp_buffer.shp"
temp_clip = arcpy.env.scratchFolder + "/temp_boundaries.shp"
temp_impervious = "temp_impervious.tif"
temp_raster = arcpy.env.scratchFolder + "/temp_raster.tif"

print("\nSETTING DEFAULT VALUES")
print("Setting snap raster")
arcpy.env.snapRaster = impervious_raster
print("Retrieving NLCD spatial reference")
spatial_ref = arcpy.Describe(impervious_raster).spatialReference

print("\nPROCESSING", impervious_year, "IMPERVIOUS DATA")
print("Setting clip boundaries")
print("\tAdding 30m buffer")
arcpy.analysis.Buffer(
    in_features=clip_boundaries,
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
print("Per basin")
df_acres = calc_stats.calc_percent(
    in_geoscale=basins,
    geoscale_field=basins_field,
    in_raster=temp_impervious,
    raster_year=impervious_year
)

print("Per HUC10")
df_temp = calc_stats.calc_percent(
    in_geoscale=huc10,
    geoscale_field=huc10_field,
    in_raster=temp_impervious,
    raster_year=impervious_year
)
df_acres = pd.concat([df_acres, df_temp])

print("Per HUC12")
df_temp = calc_stats.calc_percent(
    in_geoscale=huc12,
    geoscale_field=huc12_field,
    in_raster=temp_impervious,
    raster_year=impervious_year
)
df_acres = pd.concat([df_acres, df_temp])

print("Per study area")
df_temp = calc_stats.calc_percent(
    in_geoscale=studyarea,
    geoscale_field=studyarea_field,
    in_raster=temp_impervious,
    raster_year=impervious_year
)
df_acres = pd.concat([df_acres, df_temp])

print("Per state per study area")
df_temp = calc_stats.calc_percent(
    in_geoscale=state_studyarea,
    geoscale_field=state_field,
    in_raster=temp_impervious,
    raster_year=impervious_year
)
df_acres = pd.concat([df_acres, df_temp])

print("Per town")
df_temp = calc_stats.calc_percent(
    in_geoscale=town,
    geoscale_field=town_field,
    in_raster=temp_impervious,
    raster_year=impervious_year
)
df_acres = pd.concat([df_acres, df_temp])

print("Per town per study area")
df_temp = calc_stats.calc_percent(
    in_geoscale=town_studyarea,
    geoscale_field=town_studyarea_field,
    in_raster=temp_impervious,
    raster_year=impervious_year
)
df_acres = pd.concat([df_acres, df_temp])

print("\nDOWNLOADING FILES")
print("Saving csv")
df_acres.to_csv(csv_folder / csv_final)

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
print("\nDONE")
