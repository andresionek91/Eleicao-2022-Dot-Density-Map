import os

import aws_cdk as cdk

from src.data_processing.config import Config
from src.data_processing.stack import DataProcessingStack


app = cdk.App()

DataProcessingStack(
    scope=app,
    id="Eleicoes2022-DataProcessing",
    env=cdk.Environment(
        account=os.environ.get("AWS_ACCOUNT_ID", "0123456789"),
        region="us-east-1",
    ),
    config=Config(),  # type: ignore
)

app.synth()
