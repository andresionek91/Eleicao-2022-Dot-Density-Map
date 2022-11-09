import ast
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
from boto3.dynamodb.conditions import Attr
from boto3.dynamodb.conditions import Key
from synloc import kNNResampler
from synloc.tools import stochastic_rounder
from synthia import FPCADataGenerator


logger = Logger()
tracer = Tracer()
logging.basicConfig(level=logging.INFO)

dynamodb = boto3.resource("dynamodb")
firehose = boto3.client("firehose")


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
    cep: str
    votos: int
    numero_candidato: int


def get_geo_data(cep):
    devices_table = dynamodb.Table("geo_ceps")
    response = devices_table.get_item(Key={"cep": cep})
    item = ast.literal_eval(response.get("Item", {}).get("geo", "[]"))

    if len(item) > 30:
        df = pd.read_json(json.dumps(item))
        return df

    items = []
    for idx in range(10):
        response = devices_table.get_item(Key={"cep": f"{cep[:-1]}{idx}"})
        item = ast.literal_eval(response.get("Item", {}).get("geo", "[]"))
        items += item

    if len(items) > 30:
        df = pd.read_json(json.dumps(items))
        return df

    items = []
    for idx in range(100):
        response = devices_table.get_item(Key={"cep": f"{cep[:-2]}{str(idx).zfill(2)}"})
        item = ast.literal_eval(response.get("Item", {}).get("geo", "[]"))
        items += item

    df = pd.read_json(json.dumps(items))
    return df


@logger.inject_lambda_context
@tracer.capture_lambda_handler
@event_parser(model=Event)
def handler(event: Event, context: LambdaContext) -> None:
    """Enrich geo data and send to firehose"""

    logger.info(f"Processing event: {event}")

    synth_data = generate_syntethic_geo_data(get_geo_data(event.cep), size=event.votos, K=8)

    synth_data["cep"] = event.cep
    synth_data["numero_candidato"] = event.numero_candidato
    synth_data = synth_data[["cep", "numero_candidato", "latitude", "longitude"]]

    records = synth_data.to_dict("records")
    logger.info(f"records: {records}")

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
