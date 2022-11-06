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
df = df[["NR_ZONA", "NR_SECAO", "NM_LOCAL_VOTACAO", "DS_LOCAL_VOTACAO_ENDERECO", "NM_MUNICIPIO", "SG_UF"]]
df.columns = [
    "ZONA",
    "SECAO",
    "LOCAL",
    "ENDERECO",
    "MUNICIPIO",
    "UF",
]

df["CEP"] = None

# Join com bases de dados dos TREs para pegar os CEPs dos locais de votação
df = df.set_index(["ZONA", "SECAO", "UF"])
for uf in ["ES", "RJ", "SC"]:
    enderecos = pd.read_csv(
        f"data/processed/addresses_information/TRE-{uf}.csv",
        sep=";",
        encoding="utf-8",
        dtype={
            0: int,
            1: int,
            2: str,
            3: str,
            4: str,
            5: str,
            6: str,
        },
        header=0,
    )
    enderecos = enderecos.set_index(["ZONA", "SECAO", "UF"])

    df = df.join(enderecos, rsuffix=f"_{uf}", how="left")


# Join para CE é um pouco diferente, pois não temos as seções
df = df.reset_index()
df = df.set_index(["ZONA", "ENDERECO", "MUNICIPIO", "UF"])
enderecos = pd.read_csv(
    "data/processed/addresses_information/TRE-CE.csv",
    sep=";",
    encoding="utf-8",
    dtype={
        0: str,
        1: str,
        2: str,
        3: str,
        4: str,
        5: str,
        6: str,
    },
    header=0,
)
enderecos = enderecos.set_index(["ZONA", "ENDERECO", "MUNICIPIO", "UF"])
df = df.join(enderecos, rsuffix="_CE", how="left")


# Consolida os CEPs em uma única coluna
df["CEP"] = df["CEP_ES"].fillna("") + df["CEP_RJ"].fillna("") + df["CEP_SC"].fillna("") + df["CEP_CE"].fillna("")

# Seleciona somente colunas relevantes
df = df.reset_index()

df = df[
    [
        "LOCAL",
        "ENDERECO",
        "MUNICIPIO",
        "CEP",
        "UF",
    ]
]

df["CEP"] = df["CEP"].replace("", np.nan)

df = df.drop_duplicates()

df.to_csv(
    "data/processed/secoes_eleitorais_deduplicadas.csv",
    sep=";",
    encoding="utf-8",
    index=False,
    header=True,
)
