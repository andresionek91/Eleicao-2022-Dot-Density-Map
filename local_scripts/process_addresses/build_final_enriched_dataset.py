import pandas as pd


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

osm_df = pd.read_csv(
    filepath_or_buffer="data/processed/enriched_osm_secoes.csv",
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
osm_df = osm_df.set_index(["ENDERECO", "MUNICIPIO", "UF"])
df = df.set_index(["ENDERECO", "MUNICIPIO", "UF"])

df = df.join(osm_df, rsuffix="_2", how="left")
df = df.reset_index()
df["CEP"] = df["CEP"].fillna("")
df["CEP_2"] = df["CEP_2"].fillna("")
df["CEP"] = df[["CEP", "CEP_2"]].apply(lambda x: x[1] if not x[0] else x[0], axis=1)
df = df[["ENDERECO", "MUNICIPIO", "UF", "LOCAL", "CEP"]]


print(df[df["CEP"] == ""].shape)

cidades_df = pd.read_csv(filepath_or_buffer="data/raw/cep_by_cidade.csv", encoding="utf-8", sep="\t", header=None)
cidades_df = cidades_df[[1, 2, 3]]
cidades_df.columns = [
    "CEP",
    "MUNICIPIO",
    "UF",
]

cidades_df["CEP"] = cidades_df["CEP"].str.replace("-", "")
cidades_df["MUNICIPIO"] = cidades_df["MUNICIPIO"].str.upper()

cidades_df["UF"] = cidades_df["UF"].map(
    {
        "Minas Gerais": "MG",
        "Sao Paulo": "SP",
        "Rio Grande do Sul": "RS",
        "Bahia": "BA",
        "Parana": "PA",
        "Santa Catarina": "SC",
        "Goias": "GO",
        "Paraiba": "PB",
        "Piaui": "PI",
        "Maranhao": "MA",
        "Pernambuco": "PE",
        "Ceara": "CE",
        "Rio Grande do Norte": "RN",
        "Para": "PA",
        "Tocantins": "TO",
        "Mato Grosso": "MG",
        "Alagoas": "AL",
        "Rio de Janeiro": "RJ",
        "Mato Grosso do Sul": "MS",
        "Espirito Santo": "ES",
        "Sergipe": "SE",
        "Amazonas": "AM",
        "Rondonia": "RO",
        "Acre": "AC",
        "Distrito Federal": "DF",
        "Amapa": "AP",
        "Roraima": "RO",
    }
)

cidades_df = cidades_df.set_index(["MUNICIPIO", "UF"])
df = df.set_index(["MUNICIPIO", "UF"])
df = df.join(cidades_df, rsuffix="_2", how="left")
df = df.reset_index()

df["CEP"] = df[["CEP", "CEP_2"]].apply(
    lambda x: x[1] if not x[0] else x[0],
    axis=1,
)
df = df[["ENDERECO", "MUNICIPIO", "UF", "LOCAL", "CEP"]]

print(df)
print(df[df["CEP"] == ""].shape)

df.to_csv("data/enriched/locais_de_votacao_com_cep.csv", index=False, header=True, encoding="utf-8")
