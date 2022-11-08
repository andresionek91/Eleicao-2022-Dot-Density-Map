import pandas as pd

from synloc import kNNResampler
from synloc.tools import stochastic_rounder
from synthia import FPCADataGenerator


class LocalFPCA(kNNResampler):
    def __init__(self, data, K=30, normalize=True, clipping=True, Args_NearestNeighbors={}):
        super().__init__(data, K, normalize, clipping, Args_NearestNeighbors, method=self.method)

    def method(self, data):
        generator = FPCADataGenerator()
        generator.fit(data, n_fpca_components=2)
        return generator.generate(1)[0]


def generate_syntethic_geo_data(df_sample, size, K):
    resampler = LocalFPCA(data=df_sample, K=K)
    return resampler.fit(size)


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


df = pd.read_csv(
    filepath_or_buffer="data/enriched/votos_por_secao_com_cep.csv",
    encoding="utf-8",
    header=0,
    dtype={
        0: int,
        1: int,
        2: str,
        3: str,
        4: str,
        5: str,
        6: str,
        7: int,
        8: int,
        9: str,
        10: int,
    },
)

df = df[df.TURNO == 2]
df["CEP"] = df["CEP"].str[:-4]

df = df[["CEP", "TURNO", "NUMERO_CANDIDATO", "VOTOS"]]
df = df.groupby(["CEP", "TURNO", "NUMERO_CANDIDATO"]).sum()
df = df.reset_index()
total_rows = df.shape[0]

for row in df.itertuples():
    print(f"Processing row {row.Index} of {total_rows}")
    sub_geo_ceps_df = geo_ceps_df[geo_ceps_df["cep"] == row.CEP]
    try:
        synth_data = generate_syntethic_geo_data(sub_geo_ceps_df[["latitude", "longitude"]], size=row.VOTOS, K=10)
    except:
        try:
            synth_data = generate_syntethic_geo_data(sub_geo_ceps_df[["latitude", "longitude"]], size=row.VOTOS, K=2)
        except:
            synth_data = generate_syntethic_geo_data(sub_geo_ceps_df[["latitude", "longitude"]], size=row.VOTOS, K=1)
    synth_data["cep"] = row.CEP
    synth_data["turno"] = row.TURNO
    synth_data["numero_candidato"] = row.NUMERO_CANDIDATO
    synth_data = synth_data[["cep", "turno", "numero_candidato", "latitude", "longitude"]]
    synth_data.to_csv("data/enriched/votos_synth_cep_geo.csv", mode="a", header=False, index=False)
