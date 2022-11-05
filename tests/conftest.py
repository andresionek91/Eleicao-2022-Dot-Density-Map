import json
import os

import aws_cdk as cdk
import pytest

from aws_cdk.assertions import Template

from src.data_processing.config import Config
from src.data_processing.stack import DataProcessingStack


@pytest.fixture(scope="session")
def dummy_app_fixture():
    cdk_context = os.path.join(os.getcwd(), "cdk.context.json")

    with open(cdk_context, "r") as file:
        context = json.loads(file.read())

    return cdk.App(context=context)


@pytest.fixture(scope="session")
def dummy_stack_fixture(dummy_app_fixture):
    return DataProcessingStack(
        scope=dummy_app_fixture,
        id="TestGraphql",
        env=cdk.Environment(account=os.environ.get("AWS_ACCOUNT_ID", "0123456789"), region="us-east-1"),
        config=Config(),
    )


@pytest.fixture(scope="session")
def template_fixture(dummy_stack_fixture):
    return Template.from_stack(dummy_stack_fixture)
