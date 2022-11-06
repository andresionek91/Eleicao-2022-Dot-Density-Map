import json
import logging
import time

import boto3
import pandas as pd


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

pd.set_option("display.max_rows", 500)
pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 1000)

client = boto3.client("lambda")

df = pd.read_csv(
    filepath_or_buffer="data/processed/secoes_eleitorais_deduplicadas.csv",
    encoding="utf-8",
    sep=";",
    header=0,
    dtype={
        0: str,
        1: str,
        2: str,
        3: str,
        4: str,
    },
)

df = df[df["CEP"].isnull()]

# I ran some scripts locally before creating the lambda function in AWS.
# I'm removing the addresses that I already have the CEP to avoid duplicating the fetch in OSM
df2 = pd.read_csv(
    filepath_or_buffer="data/raw/addresses-cep.csv",
    encoding="utf-8",
    sep=",",
    header=0,
    dtype={
        0: str,
        1: str,
        2: str,
        3: str,
    },
)
df2 = df2.set_index(["ENDERECO", "MUNICIPIO", "UF"])
df = df.set_index(["ENDERECO", "MUNICIPIO", "UF"])
df = df.join(df2, rsuffix="_2", how="left")
df = df.reset_index()

df["CEP"] = df["CEP_2"]
df = df[["ENDERECO", "MUNICIPIO", "UF", "LOCAL", "CEP"]]

df = df[df["CEP"].isnull()]

df.to_csv("data/processed/secoes_eleitorais_sem_cep.csv", header=True, index=False, sep=";", encoding="utf-8")

total_size = df.shape[0]

for idx, chunk in enumerate(
    pd.read_csv(
        filepath_or_buffer="data/processed/secoes_eleitorais_sem_cep.csv",
        encoding="utf-8",
        sep=";",
        header=0,
        chunksize=10,
    )
):
    logger.info(f"processing chunk {idx}/{total_size/10}")
    df = chunk
    df = df.rename(
        columns={
            "LOCAL": "nome_local_votacao",
            "ENDERECO": "endereco_local_votacao",
            "MUNICIPIO": "municipio_local_votacao",
            "UF": "uf_local_votacao",
        }
    )
    df = df[
        [
            "nome_local_votacao",
            "endereco_local_votacao",
            "municipio_local_votacao",
            "uf_local_votacao",
        ]
    ]

    records = df.to_dict("records")
    payload = {"items": records}

    response = client.invoke(
        FunctionName="Eleicoes2022-DataProcessi-EnrichAddressesFunctionC-Tm2cy50QQsUA",
        InvocationType="Event",
        Payload=json.dumps(payload),
    )
    time.sleep(3)
