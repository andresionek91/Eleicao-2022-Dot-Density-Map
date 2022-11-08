from aws_cdk import aws_dynamodb as dynamodb
from constructs import Construct


class DynamoDbConstruct(Construct):
    """Construct"""

    def __init__(
        self,
        scope: Construct,
        id: str,
    ) -> None:
        super().__init__(scope, id)

        self.table = dynamodb.Table(
            scope=self,
            id="GeoCepsTable",
            table_name="geo_ceps",
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            partition_key=dynamodb.Attribute(name="cep", type=dynamodb.AttributeType.STRING),
        )
