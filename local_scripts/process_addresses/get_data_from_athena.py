import pandas as pd

from pyathena import connect


conn = connect(
    s3_staging_dir="s3://eleicoes2022-dataprocess-athenaresultsbucketfd0f4-1152qlfm6eaa5/eleicoes_workgroup/results/",
    region_name="us-east-1",
)

with open("local_scripts/athena_query.sql", "r") as f:
    query = f.read()

df = pd.read_sql_query(query, conn)
df.columns = ["ENDERECO", "MUNICIPIO", "UF", "CEP"]
df.to_csv(
    "data/processed/enriched_osm_secoes.csv",
    header=True,
    index=False,
)
