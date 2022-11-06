import json

import boto3
import pandas as pd


pd.set_option("display.max_rows", 500)
pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 1000)

client = boto3.client("lambda")

# Run deduplicate_secoes_eleitorais.py before executing this script
for chunk in pd.read_csv(
    filepath_or_buffer="data/secoes_eleitorais_deduplicadas.csv",
    encoding="latin-1",
    sep=";",
    header=0,
    chunksize=200,
    nrows=10000,
):
    df = chunk
    df = df.rename(
        columns={
            "NR_ZONA": "nr_zona",
            "NR_SECAO": "nr_secao",
            "NM_LOCAL_VOTACAO": "nome_local_votacao",
            "DS_LOCAL_VOTACAO_ENDERECO": "endereco_local_votacao",
            "NM_MUNICIPIO": "municipio_local_votacao",
            "SG_UF": "uf_local_votacao",
        }
    )
    df = df[
        [
            "nr_zona",
            "nr_secao",
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
