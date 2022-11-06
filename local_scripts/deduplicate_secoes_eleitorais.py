import pandas as pd


pd.set_option("display.max_rows", 500)
pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 1000)


# Create a data directory and save election results file from TSE:
# https://dadosabertos.tse.jus.br/
df = pd.read_csv(
    filepath_or_buffer="data/votacao_secao_2022_BR.csv",
    encoding="latin-1",
    sep=";",
    header=0,
)

df = df[(df.ANO_ELEICAO == 2022) & (df.TP_ABRANGENCIA == "F")]
df = df[
    [
        "NR_ZONA",
        "NR_SECAO",
        "NM_LOCAL_VOTACAO",
        "DS_LOCAL_VOTACAO_ENDERECO",
        "NM_MUNICIPIO",
        "SG_UF",
        "NM_UE",
    ]
]

df = df.drop_duplicates(
    [
        "NR_ZONA",
        "NR_SECAO",
        "NM_LOCAL_VOTACAO",
        "DS_LOCAL_VOTACAO_ENDERECO",
        "NM_MUNICIPIO",
    ]
)
df.to_csv("data/secoes_eleitorais_deduplicadas.csv", sep=";", encoding="latin-1", index=False, header=True)
