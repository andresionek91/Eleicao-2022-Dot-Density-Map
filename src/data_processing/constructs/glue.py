from aws_cdk import aws_glue_alpha as glue
from aws_cdk import aws_s3 as s3
from constructs import Construct


class GlueConstruct(Construct):
    """Construct"""

    def __init__(
        self,
        scope: Construct,
        id: str,
        source_bucket: s3.Bucket,
    ) -> None:
        super().__init__(scope, id)

        self.database = glue.Database(
            scope=self,
            id="Database",
            database_name="eleicoes_2022",
        )

        self.table = glue.Table(
            scope=self,
            id="SecoesAddressesTable",
            database=self.database,
            table_name="secoes_enriched_addresses",
            data_format=glue.DataFormat.JSON,
            enable_partition_filtering=True,
            compressed=True,
            bucket=source_bucket,
            s3_prefix="secoes_enriched_addresses/",
            columns=[
                glue.Column(
                    name="nr_zona", type=glue.Schema.STRING
                ),  # TODO: Remove if starting fresh, as it is not used anymore
                glue.Column(
                    name="nr_secao", type=glue.Schema.STRING
                ),  # TODO: Remove if starting fresh, as it is not used anymore
                glue.Column(name="nome_local_votacao", type=glue.Schema.STRING),
                glue.Column(name="endereco_local_votacao", type=glue.Schema.STRING),
                glue.Column(name="municipio_local_votacao", type=glue.Schema.STRING),
                glue.Column(name="uf_local_votacao", type=glue.Schema.STRING),
                glue.Column(name="lat", type=glue.Schema.STRING),
                glue.Column(name="postcode", type=glue.Schema.STRING),
                glue.Column(name="street", type=glue.Schema.STRING),
                glue.Column(name="district", type=glue.Schema.STRING),
                glue.Column(name="city", type=glue.Schema.STRING),
                glue.Column(name="countrycode", type=glue.Schema.STRING),
                glue.Column(name="enrichment quality", type=glue.Schema.STRING),
            ],
            partition_keys=[glue.Column(name="date", type=glue.Schema.DATE)],
        )
