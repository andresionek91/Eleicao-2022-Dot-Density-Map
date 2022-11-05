import aws_cdk as cdk

from constructs import Construct

from src.data_processing.config import Config


class DataProcessingStack(cdk.Stack):
    """Data Processing Stack"""

    def __init__(self, scope: Construct, id: str, config: Config, **kwargs) -> None:
        description = "Data Processing Eleicoes 2022"
        super().__init__(scope, id, description=description, **kwargs)

        # Add tags to everything in this stack
        cdk.Tags.of(self).add(key="stack", value=self.stack_name)
        cdk.Tags.of(self).add(key="project", value="eleicoes-2022")
