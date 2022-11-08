import boto3
import pandas as pd


def load_data(df, dynamodb=None):
    dynamodb = boto3.resource("dynamodb")

    devices_table = dynamodb.Table("geo_cep")
    # Loop through all the items and load each
    for row in df.itertuples():
        record = {"cep": row.cep, "latitude": row.latitude, "longitude": row.latitude}
        print(record)
        devices_table.put_item(Item=record)


if __name__ == "__main__":
    # open file and read all the data in it

    geo_ceps_df = pd.read_csv(
        filepath_or_buffer="data/raw/geolocation/cep_geo.csv",
        encoding="utf-8",
        sep="|",
        header=0,
        na_values="-",
        dtype={
            0: str,
            1: float,
            2: float,
        },
    )
    geo_ceps_df = geo_ceps_df.dropna()
    geo_ceps_df["cep"] = geo_ceps_df["cep"].str[:-4]

    load_data(geo_ceps_df)
