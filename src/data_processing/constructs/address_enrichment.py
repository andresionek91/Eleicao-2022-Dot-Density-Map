import aws_cdk as cdk

from aws_cdk import aws_iam as iam
from aws_cdk import aws_kinesisfirehose_alpha as firehose
from aws_cdk import aws_kinesisfirehose_destinations_alpha as destinations
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_lambda_python_alpha as lambda_python
from aws_cdk import aws_s3 as s3
from constructs import Construct


class AddressEnrichmentConstruct(Construct):
    """Construct"""

    def __init__(
        self,
        scope: Construct,
        id: str,
        destination_bucket: s3.Bucket,
    ) -> None:
        super().__init__(scope, id)

        destination = destinations.S3Bucket(
            bucket=destination_bucket,
            buffering_interval=cdk.Duration.minutes(amount=10),
            buffering_size=cdk.Size.mebibytes(amount=20),
            compression=destinations.Compression.GZIP,
            data_output_prefix="secoes_enriched_addresses/date=!{timestamp:yyyy}-!{timestamp:MM}-!{timestamp:dd}/",
            error_output_prefix="error/secoes_enriched_addresses/",
            logging=True,
        )

        self.delivery_stream = firehose.DeliveryStream(
            scope=self,
            id="EnrichAddressesFirehose",
            destinations=[destination],
        )

        self.function = lambda_python.PythonFunction(
            scope=self,
            id="EnrichAddressesFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler",
            entry="src/data_processing/functions/enrich_addresses",
            environment={"delivery_stream_name": self.delivery_stream.delivery_stream_name},
            timeout=cdk.Duration.seconds(amount=30),
            memory_size=128,
            dead_letter_queue_enabled=True,
        )

        self.function.add_to_role_policy(
            statement=iam.PolicyStatement(
                actions=["firehose:PutRecord", "firehose:PutRecordBatch"],
                effect=iam.Effect.ALLOW,
                resources=[self.delivery_stream.delivery_stream_arn],
            )
        )

        self.delivery_stream.grant_put_records(self.function)
