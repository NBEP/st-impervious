import arcpy


def prep_geoscale(in_features, in_field, out_features, out_coor_system):
    """
    prep_geoscale() projects input vectors to Albers Equal Conical Area and converts them to a raster.

    :param in_features: Path and file name for input vector.
    :param in_field: String. Field used to set raster value. All other fields will be dropped.
    :param out_features: Path and file name for output raster.
    :param out_coor_system: Output coordinate system.
    """
    temp_shp = arcpy.env.scratchFolder + "/temp_projection.shp"

    print("\tProjecting to Albers Equal Conical Area")
    arcpy.management.Project(
        in_dataset=in_features,
        out_dataset=temp_shp,
        out_coor_system=out_coor_system
    )

    print("\tSaving as raster")
    arcpy.conversion.PolygonToRaster(
        in_features=temp_shp,
        value_field=in_field,
        out_rasterdataset=out_features,
        cell_assignment="MAXIMUM_AREA",
        cellsize=30
    )

    return
