# import aws_cdk.aws_logs as logs

# from aws_cdk import aws_appsync_alpha as appsync
# from aws_cdk import aws_certificatemanager as acm
# from aws_cdk import aws_route53 as route53
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from src.data_processing.config import Config


class Construct(Construct):
    """Construct"""

    def __init__(
        self,
        scope: Construct,
        id: str,
        config: Config,
    ) -> None:
        super().__init__(scope, id)

        # Import values from SSM
        ssm.StringParameter.value_from_lookup(
            scope=self,
            parameter_name="/eleicoes-2022/",
        )
