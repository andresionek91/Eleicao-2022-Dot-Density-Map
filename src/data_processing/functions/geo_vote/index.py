import io
import os
import sys
import zipfile

import boto3


def load_remote_project_archive(remote_bucket, remote_file, layer_name):

    # Puts the project files from S3 in /tmp and adds to path
    project_folder = "/tmp/{0!s}".format(layer_name)
    if not os.path.isdir(project_folder):
        # The project folder doesn't exist in this cold lambda, get it from S3
        boto_session = boto3.Session()

        # Download zip file from S3
        s3 = boto_session.resource("s3")
        archive_on_s3 = s3.Object(remote_bucket, remote_file).get()

        # unzip from stream
        with io.BytesIO(archive_on_s3["Body"].read()) as zf:

            # rewind the file
            zf.seek(0)

            # Read the file as a zipfile and process the members
            with zipfile.ZipFile(zf, mode="r") as zipf:
                zipf.extractall(project_folder)

    # Add to project path
    sys.path.insert(0, project_folder)

    return True


load_remote_project_archive("sionek-eleicoes-2022-enrichment", "sklearn.zip", "sklearn")
load_remote_project_archive("sionek-eleicoes-2022-enrichment", "pandas.zip", "pandas")
load_remote_project_archive("sionek-eleicoes-2022-enrichment", "synloc.zip", "synloc")

import json
import logging

import pandas as pd

from aws_lambda_powertools import Logger
from aws_lambda_powertools import Tracer
from aws_lambda_powertools.utilities.parser import BaseModel
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.typing import LambdaContext
from synloc import LocalGaussianCopula


logger = Logger()
tracer = Tracer()
logging.basicConfig(level=logging.INFO)

dynamodb = boto3.resource("dynamodb")
firehose = boto3.resource("firehose")


def generate_syntethic_geo_data(df_sample, size, K):
    resampler = LocalGaussianCopula(data=df_sample, K=K)
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
