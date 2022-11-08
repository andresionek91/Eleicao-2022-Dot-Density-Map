import numpy as np
import pandas as pd


pd.set_option("display.max_rows", 500)
pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 1000)


# Create a data directory and save election results file from TSE:
# https://dadosabertos.tse.jus.br/
df = pd.read_csv(filepath_or_buffer="data/raw/votacao_secao_2022_BR.csv", encoding="latin-1", sep=";", header=0)

# Filtra dados 2022, eleição para presidente, exclui zonas eleitorais do exterior
df = df[(df.ANO_ELEICAO == 2022) & (df.TP_ABRANGENCIA == "F") & (df.SG_UF != "ZZ")]

# Seleciona colunas e renomeia
df = df[
    [
        "NR_ZONA",
        "NR_SECAO",
        "NM_LOCAL_VOTACAO",
        "DS_LOCAL_VOTACAO_ENDERECO",
        "NM_MUNICIPIO",
        "SG_UF",
        "NR_TURNO",
        "NR_VOTAVEL",
        "NM_VOTAVEL",
        "QT_VOTOS",
    ]
]
df.columns = [
    "ZONA",
    "SECAO",
    "LOCAL",
    "ENDERECO",
    "MUNICIPIO",
    "UF",
    "TURNO",
    "NUMERO_CANDIDATO",
    "CANDIDATO",
    "VOTOS",
]

ceps = pd.read_csv(
    "data/enriched/locais_de_votacao_com_cep.csv",
    header=0,
    encoding="utf-8",
    dtype={0: str, 1: str, 2: str, 3: str, 4: str},
)

ceps = ceps.set_index(["ENDERECO", "LOCAL", "MUNICIPIO", "UF"])
df = df.set_index(["ENDERECO", "LOCAL", "MUNICIPIO", "UF"])
df = df.join(ceps, rsuffix="_2", how="left")
df = df.reset_index()

df = df[
    ["ZONA", "SECAO", "LOCAL", "ENDERECO", "CEP", "MUNICIPIO", "UF", "TURNO", "NUMERO_CANDIDATO", "CANDIDATO", "VOTOS"]
]

df.to_csv("data/enriched/votos_por_secao_com_cep.csv", encoding="utf-8", header=True, index=False)
