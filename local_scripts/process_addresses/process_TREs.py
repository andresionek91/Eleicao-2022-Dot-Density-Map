import pandas as pd


pd.set_option("display.max_rows", 500)
pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 1000)

# TRE CE - https://www.tre-ce.jus.br/o-tre/zonas-eleitorais/locais-de-votacao-por-municipio-e-zona
df = pd.read_csv("data/raw/addresses_information/TRE-CE.csv", sep="\t", encoding="utf-8", header=0)

df["UF"] = "CE"
df["ZONA"] = df["Zona"]
df["SECAO"] = None
df["LOCAL"] = df["Local de Votação"]
df["ENDERECO"] = df["Endereço"]
df["MUNICIPIO"] = df["Município"]
df["CEP"] = df["CEP"]

df = df[["ZONA", "SECAO", "LOCAL", "ENDERECO", "MUNICIPIO", "UF", "CEP"]]
df.to_csv("data/processed/addresses_information/TRE-CE.csv", sep=";", encoding="utf-8", index=False)


# TRE ES - https://www.tre-es.jus.br/eleitor/titulo-e-local-de-votacao/arq/rpt-secoes-xls-202201011300
df = pd.read_csv("data/raw/addresses_information/TRE-ES.csv", sep=",", encoding="utf-8", header=0)
df["UF"] = "ES"
df["ZONA"] = df["num_zon"]
df["SECAO"] = df["num_secao"]
df["LOCAL"] = df["nom_local"]
df["ENDERECO"] = df["des_endereco"]
df["MUNICIPIO"] = df["nom_localidade"]
df["CEP"] = df["num_cep"]

df = df[["ZONA", "SECAO", "LOCAL", "ENDERECO", "MUNICIPIO", "UF", "CEP"]]
df.to_csv("data/processed/addresses_information/TRE-ES.csv", sep=";", encoding="utf-8", index=False)


# TRE RJ - https://www.tre-rj.jus.br/eleicoes/eleicoes-plebiscitos-e-referendos/eleicoes-2022/locais-de-votacao-e-atendimento-ao-eleitor/arquivos-locais-de-votacao/locais-de-votacao-e-secoes-eleitorais-do-estado-do-rio-de-janeiro-2o-turno-28-10 # noqa
df = pd.read_csv("data/raw/addresses_information/TRE-RJ.csv", sep=",", encoding="utf-8", header=0)
df["UF"] = "RJ"
df["ZONA"] = df["NUM_ZONA"]
df["SECAO"] = df["SECOES"].str.split(",")
df["LOCAL"] = df["NOM_LOCAL"]
df["ENDERECO"] = df[["DES_ENDERECO"]]
df["MUNICIPIO"] = df["NOM_LOCALIDADE"]
df["CEP"] = df["NUM_CEP"]

df = df.explode("SECAO")

df = df[["ZONA", "SECAO", "LOCAL", "ENDERECO", "MUNICIPIO", "UF", "CEP"]]
df.to_csv("data/processed/addresses_information/TRE-RJ.csv", sep=";", encoding="utf-8", index=False)


# TRE SC - https://apps.tre-sc.jus.br/dadosabertos-api/lista-locais/csv
df = pd.read_csv("data/raw/addresses_information/TRE-SC.csv", sep=",", encoding="utf-8", header=0)

df["UF"] = "SC"
df["ZONA"] = df["zona_eleitoral"]
df["SECAO"] = df["secoes_aptos"].str.split(",")

df = df.explode("SECAO")

df["SECAO"] = df["SECAO"].str.split("(").str[0]

df["LOCAL"] = df["nome_local_votacao"]
df["ENDERECO"] = df[["endereco"]]
df["MUNICIPIO"] = df["municipio"]
df["CEP"] = df["cep"]

df = df[["ZONA", "SECAO", "LOCAL", "ENDERECO", "MUNICIPIO", "UF", "CEP"]]
df.to_csv("data/processed/addresses_information/TRE-SC.csv", sep=";", encoding="utf-8", index=False)
