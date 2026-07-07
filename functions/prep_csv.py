import pandas as pd


def add_huc_name(df, huc_field, ref_csv):
    """
    add_huc_name() updates the input dataframe by adding a column with a matching HUC name or number.

    :param df: Input dataframe.
    :param huc_field: String. Name of field containing HUC name or number.
    :param ref_csv: String. Path to reference CSV with paired columns for HUC number and HUC name.
    """

    print("\tAdding HUC name")
    df.rename(columns={"Geoscale_Name": huc_field}, inplace=True)
    if huc_field in ["HUC10", "HUC12"]:
        df[huc_field] = df[huc_field].astype(float)
    df_ref = pd.read_csv(ref_csv)
    df = df.join(df_ref.set_index(huc_field), on=huc_field)

    return df


def split_geoscale(in_df, geoscale, source_year, nbep_year, out_path, csv_prefix="IMPERVIOUS_"):
    """
    split_geoscale() split the input dataframe by geoscale and saves each geoscale to a different csv file.

    :param in_df: Input dataframe.
    :param geoscale: String. Name of geoscale to filter column "Geoscale" by. Examples: "Basin", "HUC10"
    :param nbep_year: Integer. Current year.
    :param source_year: String or integer. Data source year.
    :param out_path: Path. Location to save output csv.
    :param csv_prefix: String. Prefix to csv name. Default "IMPERVIOUS_".
    """

    print("\tFiltering data")
    df = in_df.copy()
    df = df[df["Geoscale"] == geoscale]

    print("\tDropping empty columns")
    df.dropna(how='all', axis=1, inplace=True)

    print("\tAdding metadata columns")
    df["Data_Source"] = "USGS NLCD"
    df["Source_Year"] = source_year
    df["NBEP_Year"] = nbep_year

    print("\tSaving csv")
    csv_name = csv_prefix + geoscale + "_NBEP" + str(nbep_year) + ".csv"
    out_csv = out_path / csv_name
    df.to_csv(out_csv)

    return
