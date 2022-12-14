import aws_cdk as cdk

from aws_cdk import aws_s3 as s3
from constructs import Construct

from src.data_processing.config import Config
from src.data_processing.constructs.address_enrichment import AddressEnrichmentConstruct
from src.data_processing.constructs.athena import AthenaConstruct
from src.data_processing.constructs.dynamo_db import DynamoDbConstruct
from src.data_processing.constructs.geo_vote import GeoVoteConstruct
from src.data_processing.constructs.glue import GlueConstruct


class DataProcessingStack(cdk.Stack):
    """Data Processing Stack"""

    def __init__(self, scope: Construct, id: str, config: Config, **kwargs) -> None:
        description = "Data Processing Eleicoes 2022"
        super().__init__(scope, id, description=description, **kwargs)

        self.bucket = s3.Bucket(
            scope=self,
            id="EnrichmentDataBucket",
            bucket_name="sionek-eleicoes-2022-enrichment",
        )

        self.address_enrichment = AddressEnrichmentConstruct(
            scope=self,
            id="EnrichAddresses",
            destination_bucket=self.bucket,
        )

        self.athena = AthenaConstruct(scope=self, id="Athena")
        self.dynamodb = DynamoDbConstruct(scope=self, id="DynamoDb")
        self.glue = GlueConstruct(
            scope=self,
            id="EleicoesGlue",
            source_bucket=self.bucket,
        )
        self.geo_vote = GeoVoteConstruct(
            scope=self,
            id="GeoVotes",
            destination_bucket=self.bucket,
            geo_dynamo_db_table=self.dynamodb.table,
        )
        # Add tags to everything in this stack
        cdk.Tags.of(self).add(key="stack", value=self.stack_name)
        cdk.Tags.of(self).add(key="project", value="eleicoes-2022")
