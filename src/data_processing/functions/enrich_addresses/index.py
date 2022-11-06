import json
import logging
import os

from typing import List
from urllib.parse import quote

import backoff
import boto3
import requests
import unidecode

from aws_lambda_powertools import Logger
from aws_lambda_powertools import Tracer
from aws_lambda_powertools.utilities.parser import BaseModel
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.typing import LambdaContext


logger = Logger()
tracer = Tracer()
logging.basicConfig(level=logging.INFO)

firehose = boto3.client("firehose")


class Secao(BaseModel):
    """Secao eleitoral"""

    nr_zona: str
    nr_secao: str
    nome_local_votacao: str
    endereco_local_votacao: str
    municipio_local_votacao: str
    uf_local_votacao: str


class Secoes(BaseModel):
    """Conjunto de secoes"""

    items: List[Secao]


@backoff.on_exception(backoff.expo, requests.RequestException, max_time=20)
def get_osm_data(query: str) -> dict:
    """Make a request to Photon OSM"""
    norm_query = quote(unidecode.unidecode(query))
    logger.info(f"Making request with query: {norm_query}")

    response = requests.get(f"https://photon.komoot.io/api/?q={norm_query}")
    response.raise_for_status()

    logger.info(response.text)
    return response.json()


def parse_osm_data(data: dict) -> dict:
    """Parse OSM Response"""
    return {
        "lat": data["features"][0]["geometry"]["coordinates"][0],
        "long": data["features"][0]["geometry"]["coordinates"][1],
        "postcode": data["features"][0]["properties"].get("postcode", None),
        "street": data["features"][0]["properties"].get("street", None),
        "district": data["features"][0]["properties"].get("district", None),
        "city": data["features"][0]["properties"].get("city", None),
        "countrycode": data["features"][0]["properties"].get("countrycode", None),
    }


@logger.inject_lambda_context
@tracer.capture_lambda_handler
@event_parser(model=Secoes)
def handler(event: Secoes, context: LambdaContext) -> None:
    """Get a chunk of records and enrich it using https://photon.komoot.io/api/?q={query} and send to kinesis firehose"""
    enriched_items = ""

    for item in event.items:

        try:
            # Search with full address
            query = f"{item.endereco_local_votacao} {item.municipio_local_votacao} {item.uf_local_votacao}"
            enriched = parse_osm_data(get_osm_data(query))
            enriched = {**item.dict(), **enriched, "enrichment quality": 3}
        except (KeyError, IndexError):
            enriched = None

        if not enriched:
            try:
                # Search with first part of address + city and state
                query = f"{item.endereco_local_votacao.split(',')[0]}, {item.municipio_local_votacao}, {item.uf_local_votacao}"
                enriched = parse_osm_data(get_osm_data(query))
                enriched = {**item.dict(), **enriched, "enrichment quality": 2}
            except (KeyError, IndexError):
                enriched = None

        if not enriched:
            try:
                # Search with city and state
                query = f"{item.municipio_local_votacao}, {item.uf_local_votacao}, BRASIL"
                enriched = parse_osm_data(get_osm_data(query))
                enriched = {**item.dict(), **enriched, "enrichment quality": 1}
            except (KeyError, IndexError):
                logger.warning(
                    f"Did not find any geo data for query: {item.municipio_local_votacao}, {item.uf_local_votacao}, BRASIL"
                )
                continue

        json_enriched = json.dumps(enriched) + "\n"

        enriched_items += json_enriched

    logger.info("Putting batch to firehose")
    firehose.put_record_batch(
        DeliveryStreamName=os.environ["delivery_stream_name"],
        Records=[
            {"Data": enriched_items.encode("latin-1")},
        ],
    )
