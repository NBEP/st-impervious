# ---------------------------------------------------------------------------
# 2_split_geoscales.py
# Authors: Mariel Sorlien
# Python 3.7
#
# Description:
# Combines annual impervious cover CSV files and saves a separate CSV for each geoscale.
#
# REQUIRES GIS/ARCPY
# ---------------------------------------------------------------------------

# Import modules
from pathlib import Path
import pandas as pd

from functions import prep_csv

# Set working directory, projection --------------------------------------------
base_folder = Path.cwd().parents[2] / "Data" / "int_tabulardata" / "impervious_int"

# Define variables
in_csv = [
    "IMPERVIOUS_1985_NBEP2026.csv", "IMPERVIOUS_1990_NBEP2026.csv", "IMPERVIOUS_1995_NBEP2026.csv",
    "IMPERVIOUS_2000_NBEP2026.csv", "IMPERVIOUS_2005_NBEP2026.csv", "IMPERVIOUS_2010_NBEP2026.csv",
    "IMPERVIOUS_2015_NBEP2026.csv", "IMPERVIOUS_2020_NBEP2026.csv", "IMPERVIOUS_2025_NBEP2026.csv"
]

source_year = 2026
nbep_year = 2026

# Output files
out_csv = base_folder / "IMPERVIOUS_change_2000_2025_NBEP2026.csv"

# RUN SCRIPT ----------------------------------------------------------------------------------------------------------
print("\nIMPORTING DATA")
df = pd.DataFrame()
for csv in in_csv:
    print("Reading in", csv)
    temp_csv = base_folder / csv
    df_temp = pd.read_csv(temp_csv)
    df = pd.concat([df, df_temp])
print("Sorting data by location, year")
sort_col = ["Geoscale", "Geoscale_Name", "HUC12", "HUC10", "Basins", "Study_Area", "Year"]
df.sort_values(by=sort_col, inplace=True)
df.reset_index(drop=True, inplace=True)

print("\nSPLITTING DATA BY GEOSCALE")
geoscale_list = df["Geoscale"].unique()
for geoscale in geoscale_list:
    print("By", geoscale)
    prep_csv.split_geoscale(
        in_df=df,
        geoscale=geoscale,
        nbep_year=nbep_year,
        source_year=source_year,
        out_path=base_folder
    )

print("\nDONE")
