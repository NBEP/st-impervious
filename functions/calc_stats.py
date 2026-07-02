import arcpy
import pandas as pd


def calc_percent(in_geoscale, geoscale_field, in_nlcd, nlcd_year):
    """
    calc_area() generates a table containing a breakdown of acres and percent land cover for all land classes at the
    relevant geoscale.

    :param in_geoscale: Path and file name for raster geoscale.
    :param geoscale_field: String. Name of field containing geoscale names.
    :param in_nlcd: Path and file name for NLCD raster.
    :param nlcd_year: Integer. Source year for NLCD data.
    """
    out_table = arcpy.env.scratchFolder + "/temp_table.dbf"

    print("\tCalculating percent impervious cover")
    arcpy.sa.ZonalStatisticsAsTable(
        in_zone_data=in_geoscale,
        zone_field=geoscale_field,
        in_value_raster=in_nlcd,
        out_table=out_table,
        statistics_type="MEAN"
    )

    print("\tConverting to dataframe")
    df = arcpy.da.TableToNumPyArray(
        in_table=out_table,
        field_names="*"
    )
    df = pd.DataFrame(df)

    print("\tAdding columns")
    df["Geoscale"] = geoscale_field
    df["Geoscale_Name"] = df[geoscale_field]
    df["Year"] = nlcd_year
    df.rename(columns={"MEAN": "Percent_Impervious"}, inplace=True)

    df = df[["Geoscale", "Geoscale_Name", "Year", "Percent_Impervious"]]

    return df
