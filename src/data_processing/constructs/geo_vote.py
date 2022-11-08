import aws_cdk as cdk

from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kinesisfirehose_alpha as firehose
from aws_cdk import aws_kinesisfirehose_destinations_alpha as destinations
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_lambda_python_alpha as lambda_python
from aws_cdk import aws_s3 as s3
from constructs import Construct


class GeoVoteConstruct(Construct):
    """Construct"""

    def __init__(
        self,
        scope: Construct,
        id: str,
        destination_bucket: s3.Bucket,
        geo_dynamo_db_table: dynamodb.Table,
    ) -> None:
        super().__init__(scope, id)

        destination = destinations.S3Bucket(
            bucket=destination_bucket,
            buffering_interval=cdk.Duration.minutes(amount=10),
            buffering_size=cdk.Size.mebibytes(amount=20),
            compression=destinations.Compression.GZIP,
            data_output_prefix="geo_vote/date=!{timestamp:yyyy}-!{timestamp:MM}-!{timestamp:dd}/",
            error_output_prefix="error/geo_vote/",
            logging=True,
        )

        self.delivery_stream = firehose.DeliveryStream(
            scope=self,
            id="GeoVoteFirehose",
            destinations=[destination],
        )

        sk_learn_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope=self,
            id="SkLearnLayer",
            layer_version_arn="arn:aws:lambda:us-east-1:317456194246:layer:sklearn:1",
        )

        pandas_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope=self,
            id="PandasLayer",
            layer_version_arn="arn:aws:lambda:us-east-1:317456194246:layer:pandas:1",
        )

        synloc_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope=self,
            id="SynlocLayer",
            layer_version_arn="arn:aws:lambda:us-east-1:317456194246:layer:synloc:1",
        )

        self.function = lambda_python.PythonFunction(
            scope=self,
            id="EnrichAddressesFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler",
            entry="src/data_processing/functions/geo_vote",
            environment={"delivery_stream_name": self.delivery_stream.delivery_stream_name},
            timeout=cdk.Duration.minutes(amount=5),
            memory_size=512,
            dead_letter_queue_enabled=True,
            layers=[pandas_layer],
        )

        self.function.add_to_role_policy(
            statement=iam.PolicyStatement(
                actions=["firehose:PutRecord", "firehose:PutRecordBatch"],
                effect=iam.Effect.ALLOW,
                resources=[self.delivery_stream.delivery_stream_arn],
            )
        )

        self.function.add_to_role_policy(
            statement=iam.PolicyStatement(
                actions=[
                    "dynamodb:DescribeTable",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                    "dynamodb:GetItem",
                ],
                effect=iam.Effect.ALLOW,
                resources=[geo_dynamo_db_table.table_arn],
            )
        )

        self.function.add_to_role_policy(
            statement=iam.PolicyStatement(
                actions=["s3:List*", "s3:Get*"],
                effect=iam.Effect.ALLOW,
                resources=[destination_bucket.bucket_arn, destination_bucket.arn_for_objects(key_pattern="*")],
            )
        )

        self.delivery_stream.grant_put_records(self.function)
