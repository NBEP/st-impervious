# ---------------------------------------------------------------------------
# figures.py
# Authors: Mariel Sorlien
# Python 3.11
#
# Description:
# Generates maps, graphs, and figures for presentations.
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

# FIGURE 1 - difference in impervious cover
start_year = 1985
end_year = 2025
start_raster = "impervious_int.gdb/IMPERVIOUS_" + str(start_year) + "_NBEP2026"
end_raster = "impervious_int.gdb/IMPERVIOUS_" + str(end_year) + "_NBEP2026"

out_raster = "IMPERVIOUS_" + str(start_year) + "_" + str(end_year) + "_NBEP2026.tif"

# RUN SCRIPT ----------------------------------------------------------------------------------------------------------

print("FIGURE 1 - DIFFERENCE IN IMPERVIOUS COVER")
print("Subtracting values")
raster_math = arcpy.ia.ComputeChange(
    raster1=start_raster,
    raster2=end_raster,
    define_transition_colors="FROM_COLOR"
)
raster_math.save(out_raster)

print("\nDONE")
