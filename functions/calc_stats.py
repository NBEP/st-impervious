import arcpy
import pandas as pd


def calc_percent(in_geoscale, geoscale_field, in_raster, raster_year):
    """
    calc_area() generates a table containing a breakdown of acres and percent land cover for all land classes at the
    relevant geoscale.

    :param in_geoscale: Path and file name for raster geoscale.
    :param geoscale_field: String. Name of field containing geoscale names.
    :param in_raster: Path and file name for impervious cover raster.
    :param raster_year: Integer. Source year for impervious cover data.
    """
    out_table = arcpy.env.scratchFolder + "/temp_table.dbf"
    geo_copy = arcpy.env.scratchFolder + "/temp_shp.shp"
    geo_table = arcpy.env.scratchFolder + "/temp_geotable.dbf"

    print("\tCalculating percent impervious cover")
    arcpy.sa.ZonalStatisticsAsTable(
        in_zone_data=in_geoscale,
        zone_field=geoscale_field,
        in_value_raster=in_raster,
        out_table=out_table,
        statistics_type="MEAN"
    )

    print("\tConverting to dataframe")
    df = arcpy.da.TableToNumPyArray(
        in_table=out_table,
        field_names="*"
    )
    df = pd.DataFrame(df)
    df = df[[geoscale_field, "MEAN"]]
    df.rename(columns={"MEAN": "Percent_IC"}, inplace=True)

    print("\tCalculating area (acres)")
    arcpy.management.CopyFeatures(
        in_features=in_geoscale,
        out_feature_class=geo_copy
    )
    arcpy.management.AddField(
        in_table=geo_copy,
        field_name="temp_area",
        field_type="DOUBLE"
    )
    arcpy.management.CalculateGeometryAttributes(
        in_features=geo_copy,
        geometry_property=[["temp_area", "AREA"]],
        area_unit="ACRES"
    )
    print("\tConverting to dataframe")
    arcpy.conversion.ExportTable(
        in_table=geo_copy,
        out_table=geo_table
    )
    df_acre = arcpy.da.TableToNumPyArray(
        in_table=geo_table,
        field_names="*"
    )
    df_acre = pd.DataFrame(df_acre)
    df_acre = df_acre[[geoscale_field, "temp_area"]]  # Drop extra columns
    df_acre.rename(columns={"temp_area": "Total_Acres"}, inplace=True)

    print("\tMerging dataframes")
    df = df.join(df_acre.set_index(geoscale_field), on=geoscale_field)

    print("\tUpdating columns")
    df["Geoscale"] = geoscale_field
    df["Geoscale_Name"] = df[geoscale_field]
    df["Year"] = raster_year
    df["Acres_IC"] = df["Total_Acres"] * df["Percent_IC"] / 100
    df = df[["Geoscale", "Geoscale_Name", "Year", "Percent_IC", "Acres_IC", "Total_Acres"]]

    return df
