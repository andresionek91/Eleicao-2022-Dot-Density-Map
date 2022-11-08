import json
import logging
import os

import boto3
import pandas as pd

from aws_lambda_powertools import Logger
from aws_lambda_powertools import Tracer
from aws_lambda_powertools.utilities.parser import BaseModel
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.typing import LambdaContext
from synloc import kNNResampler
from synloc.tools import stochastic_rounder
from synthia import FPCADataGenerator


logger = Logger()
tracer = Tracer()
logging.basicConfig(level=logging.INFO)

dynamodb = boto3.resource("dynamodb")
firehose = boto3.resource("firehose")


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


class Event(BaseModel):
    """Conjunto de secoes"""

    cep: str
    votos: int
    numero_candidato: int


def get_geo_data(cep):
    devices_table = dynamodb.Table("geo_ceps")
    item = devices_table.get_item(Key={"cep": cep})["Item"]
    df = pd.read_json(item["geo"])
    return df


@logger.inject_lambda_context
@tracer.capture_lambda_handler
@event_parser(model=Event)
def handler(event: Event, context: LambdaContext) -> None:
    """Enrich geo data and send to firehose"""

    logger.info("fProcessing event: {event}")

    synth_data = generate_syntethic_geo_data(get_geo_data("0100"), size=event.votos, K=10)

    synth_data["cep"] = event.cep
    synth_data["numero_candidato"] = event.numero_candidato
    synth_data = synth_data[["cep", "numero_candidato", "latitude", "longitude"]]

    records = synth_data.to_json("records")

    logger.info(f"Generated records {records}")

    data = ""
    for record in records:
        data += json.dumps(record) + "\n"

    logger.info("Putting batch to firehose")
    firehose.put_record_batch(
        DeliveryStreamName=os.environ["delivery_stream_name"],
        Records=[
            {"Data": data.encode("utf-8")},
        ],
    )
